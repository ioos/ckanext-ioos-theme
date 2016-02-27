import os
ckan_home = os.environ.get('CKAN_HOME', '/usr/lib/ckan/default')
activate_this = os.path.join(ckan_home, 'bin/activate_this.py')
execfile(activate_this, dict(__file__=activate_this))

from StringIO import StringIO
import os
import sys

app_path = os.path.dirname(__file__)
sys.path.append(app_path)

from pycsw import server


def application(env, start_response):
    """WSGI wrapper"""
    config = '/etc/ckan/default/pycsw.cfg'

    if 'PYCSW_CONFIG' in env:
        config = env['PYCSW_CONFIG']

    if env['QUERY_STRING'].lower().find('config') != -1:
        for kvp in env['QUERY_STRING'].split('&'):
            if kvp.lower().find('config') != -1:
                config = kvp.split('=')[1]

    if not os.path.isabs(config):
        config = os.path.join(app_path, config)

    if 'HTTP_HOST' in env and ':' in env['HTTP_HOST']:
        env['HTTP_HOST'] = env['HTTP_HOST'].split(':')[0]

    env['local.app_root'] = app_path

    csw = server.Csw(config, env)

    gzip = False
    if ('HTTP_ACCEPT_ENCODING' in env and
            env['HTTP_ACCEPT_ENCODING'].find('gzip') != -1):
        # set for gzip compressed response
        gzip = True

    # set compression level
    if csw.config.has_option('server', 'gzip_compresslevel'):
        gzip_compresslevel = \
            int(csw.config.get('server', 'gzip_compresslevel'))
    else:
        gzip_compresslevel = 0

    contents = csw.dispatch_wsgi()

    headers = {}

    if gzip and gzip_compresslevel > 0:
        import gzip

        buf = StringIO()
        gzipfile = gzip.GzipFile(mode='wb', fileobj=buf,
                                 compresslevel=gzip_compresslevel)
        gzipfile.write(contents)
        gzipfile.close()

        contents = buf.getvalue()

        headers['Content-Encoding'] = 'gzip'

    headers['Content-Length'] = str(len(contents))
    headers['Content-Type'] = csw.contenttype

    status = '200 OK'
    start_response(status, headers.items())

    return [contents]

if __name__ == '__main__':  # run inline using WSGI reference implementation
    from wsgiref.simple_server import make_server
    port = 8000
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    httpd = make_server('', port, application)
    print "Serving on port %d..." % port
    httpd.serve_forever()

