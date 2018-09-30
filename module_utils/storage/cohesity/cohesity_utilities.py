

def cohesity_common_argument_spec():
    return dict(
        server=dict(aliases=['cohesity_cluster', 'cluster']),
        username=dict(aliases=['cohesity_user', 'admin_name']),
        password=dict(aliases=['cohesity_password',
                               'admin_pass'], no_log=True),
        validate_certs=dict(default=True, type='bool'),
        security_token=dict(aliases=['access_token'], no_log=True),
    )
