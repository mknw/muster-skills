"""L1 native CLI contract probes using the actual pinned binary and a rejecting peer.
No Herdr server, agent, provider, SSH connection or integration is started.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import tempfile
import threading

parser = argparse.ArgumentParser()
parser.add_argument('--evidence', type=Path, required=True)
parser.add_argument('--binary', type=Path, required=True)
parser.add_argument('--sha256', required=True, help='Pinned official asset digest for the supplied platform binary')
args = parser.parse_args()
out = args.evidence.resolve()
out.mkdir(parents=True, exist_ok=True)
binary = args.binary.resolve()
digest = hashlib.sha256(binary.read_bytes()).hexdigest()
assert digest == args.sha256
records = []
with tempfile.TemporaryDirectory(prefix='native-fixture-', dir=out) as scratch:
    scratch = Path(scratch)
    # Relative socket avoids macOS's short Unix socket path limit. Both processes
    # have this reviewer-owned cwd; no user's socket or connection registry is read.
    os.chdir(scratch)
    env = {'PATH': '/usr/bin:/bin', 'HERDR_SOCKET_PATH': 'peer.sock',
           'XDG_CONFIG_HOME': str(scratch / 'config'), 'XDG_STATE_HOME': str(scratch / 'state'),
           'XDG_DATA_HOME': str(scratch / 'data'), 'HERDR_DISABLE_SOUND': '1', 'TERM': 'dumb'}

    def cli(argv):
        try:
            proc = subprocess.run([str(binary), *argv], cwd=scratch, env=env,
                                  text=True, capture_output=True, timeout=9)
        except subprocess.TimeoutExpired:
            records.append(dict(argv=argv, timeout_seconds=9))
            (out / 'native-commands.json').write_text(json.dumps(records, indent=2) + '\n')
            raise
        records.append(dict(argv=argv, returncode=proc.returncode, stdout=proc.stdout, stderr=proc.stderr))
        (out / 'native-commands.json').write_text(json.dumps(records, indent=2) + '\n')
        return proc

    version = cli(['--version'])
    assert version.returncode == 0 and version.stdout.strip() == 'herdr 0.9.5'
    proc = cli(['api', 'schema', '--json'])
    assert proc.returncode == 0
    schema = json.loads(proc.stdout)
    assert schema['protocol'] == 22 and schema['schema_version'] == 1
    (out / 'independent-native-schema.json').write_text(proc.stdout)
    records[-1]['stdout'] = 'Full schema stored in independent-native-schema.json'
    help_result = cli(['--help'])
    assert help_result.returncode == 0
    assert all(flag in help_result.stdout for flag in ['--remote', '--session', '--machine'])

    methods = {v['properties']['method']['const']: v for v in schema['schemas']['request']['oneOf']}
    prompt = 'task contract-probe / attempt fixture / source fixture\nLiteral $(echo NOT_EXECUTED) `also_not_executed` "quote" \\ end'
    cases = [
        (['workspace', 'create', '--cwd', str(scratch), '--label', 'contract-fixture', '--no-focus'], 'workspace.create', {'cwd': str(scratch)}),
        (['pane', 'split', 'w1:p1', '--direction', 'right', '--no-focus'], 'pane.split', {}),
        (['agent', 'start', 'contract-fixture', '--kind', 'codex', '--pane', 'w1:p1', '--timeout', '5000', '--', '-m', 'fixture-model'], 'agent.start', {'name': 'contract-fixture', 'kind': 'codex', 'args': ['-m', 'fixture-model']}),
        (['agent', 'prompt', 'contract-fixture', prompt, '--wait', '--until', 'idle', '--until', 'done', '--timeout', '5000'], 'agent.prompt', {'text': prompt}),
        (['agent', 'wait', 'contract-fixture', '--until', 'blocked', '--timeout', '5000'], 'agent.wait', {}),
        (['agent', 'get', 'contract-fixture'], 'agent.get', {}),
        (['pane', 'run', 'w1:p1', 'printf "%s" "fixture only"'], None, {}),
    ]
    transport = []
    for argv, method, expected in cases:
        requests = []
        errors = []
        with socket.socket(socket.AF_UNIX) as listener:
            listener.bind('peer.sock')
            listener.listen(1)
            listener.settimeout(5)
            def done():
                return bool(requests) and (method is None or requests[-1]['method'] == method)
            def serve():
                try:
                    while not done():
                        with listener.accept()[0] as conn:
                            conn.settimeout(5)
                            stream = conn.makefile('rb')
                            while True:
                                line = stream.readline()
                                if not line:
                                    break
                                req = json.loads(line)
                                with (out / 'native-peer.jsonl').open('a') as log:
                                    log.write(json.dumps({'argv': argv, 'request': req}) + '\n')
                                if req['method'] == 'ping':
                                    response = {'id': req['id'], 'result': {'type': 'pong', 'version': '0.9.5', 'protocol': 22}}
                                else:
                                    requests.append(req)
                                    response = {'id': req['id'], 'error': {'code': 'contract_probe_rejected', 'message': 'Contract peer: no effect'}}
                                conn.sendall((json.dumps(response) + '\n').encode())
                                if done():
                                    break
                except Exception as exc:
                    errors.append(repr(exc))
            thread = threading.Thread(target=serve, daemon=True)
            thread.start()
            proc = cli(argv)
            thread.join(6)
        Path('peer.sock').unlink()
        assert not errors and not thread.is_alive(), (errors, records[-1])
        assert requests, requests
        req = requests[-1]
        if method is not None:
            assert req['method'] == method, req
        assert req['method'] in methods, req
        for key, value in expected.items():
            assert req['params'][key] == value, req
        definition = methods[req['method']]['properties'].get('params', {})
        if '$ref' in definition:
            def_name = definition['$ref'].rsplit('/', 1)[1]
            declared = schema['schemas']['request']['$defs'][def_name]
            assert set(declared.get('required', [])).issubset(req['params']), req
            assert set(req['params']).issubset(declared['properties']), req
        assert proc.returncode == 1, records[-1]
        assert json.loads(proc.stderr)['error']['code'] == 'contract_probe_rejected'
        transport.append(dict(argv=argv, requests=requests, request=req, expected_error=True))

    # Usage mutations must fail before connecting to the missing private socket.
    controls = []
    for argv in [
        ['agent', 'start', 'contract-fixture', '--kind', 'codex'],
        ['agent', 'prompt', 'contract-fixture', 'fixture', '--until', 'idle'],
        ['agent', 'wait', 'contract-fixture', '--until', 'not-a-state'],
        ['--machine', 'nonexistent-probe-profile', '--session', 'review', 'agent', 'get', 'contract-fixture'],
    ]:
        proc = cli(argv)
        assert proc.returncode == 2, records[-1]
        controls.append(dict(argv=argv, returncode=proc.returncode, stderr=proc.stderr))
    # Unknown remote profile must fail closed without attempting local API fallback.
    with socket.socket(socket.AF_UNIX) as listener:
        listener.bind('peer.sock')
        listener.listen(1)
        listener.settimeout(0.2)
        proc = cli(['--machine', 'nonexistent-probe-profile', 'agent', 'get', 'contract-fixture'])
        assert proc.returncode != 0
        contacted_local = False
        try:
            conn, _ = listener.accept()
            conn.close()
            contacted_local = True
        except socket.timeout:
            pass
        assert not contacted_local
    Path('peer.sock').unlink()
    controls.append(dict(case='unknown-profile-no-local-fallback', returncode=proc.returncode,
                         stderr=proc.stderr, local_contact=False))
    # Schema declares the two JSON result containers used by the skill.
    result = schema['schemas']['success_response']['$defs']['ResponseResult']
    shapes = result.get('oneOf', result.get('anyOf', []))
    assert any('root_pane' in row.get('properties', {}) for row in shapes)
    assert any('pane' in row.get('properties', {}) for row in shapes)
    report = dict(layer='L1 actual CLI parsing/serialization with rejecting fake peer',
                  version=version.stdout.strip(), binary_sha256=digest, protocol=schema['protocol'],
                  cases=transport, negative_controls=controls, passed=len(transport)+len(controls),
                  limits='No real Herdr server, provider, model, conversation restore, SSH, Incus, skill loading, or server acceptance.')
    (out / 'native-results.json').write_text(json.dumps(report, indent=2) + '\n')
    (out / 'native-commands.json').write_text(json.dumps(records, indent=2) + '\n')
    os.chdir(out)
print(json.dumps({'passed': report['passed'], 'version': report['version'], 'layer': report['layer']}))
