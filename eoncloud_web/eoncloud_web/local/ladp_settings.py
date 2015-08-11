#-*- coding=utf-8 -*-
import ldap
from django_auth_ldap.config import LDAPSearch

# Baseline configuration.
AUTH_LDAP_SERVER_URI = "ldap://127.0.0.1:389/"

AUTH_LDAP_BIND_DN = "uid=admin,ou=system"
AUTH_LDAP_BIND_PASSWORD = "12345"

AUTH_LDAP_USER_SEARCH = LDAPSearch("ou=users,dc=eoncloud,dc=com",
                                   ldap.SCOPE_SUBTREE, "(cn=%(user)s)")
# or perhaps:
# AUTH_LDAP_USER_DN_TEMPLATE = "uid=%(user)s,ou=users,dc=eoncloud,dc=com"

AUTH_LDAP_USER_ATTR_MAP = {
    "first_name": "givenName",
    "last_name": "sn",
    "email": "mail"
}

AUTH_LDAP_ALWAYS_UPDATE_USER = True

# Group relate configuration

# AUTH_LDAP_FIND_GROUP_PERMS = True
# AUTH_LDAP_MIRROR_GROUPS = True

# AUTH_LDAP_GROUP_SEARCH = LDAPSearch("ou=groups,dc=bluven,dc=me",
#                                     ldap.SCOPE_SUBTREE,
#                                     (objectClass=groupOfNames)")
# AUTH_LDAP_GROUP_TYPE = GroupOfNamesType(name_attr='cn')

# Simple group restrictions
# AUTH_LDAP_REQUIRE_GROUP = "ou=system"
# AUTH_LDAP_DENY_GROUP = "ou=system"


# Cache group memberships for an hour to minimize LDAP traffic
#AUTH_LDAP_CACHE_GROUPS = False
#AUTH_LDAP_GROUP_CACHE_TIMEOUT = 3600
# AUTH_LDAP_BIND_AS_AUTHENTICATING_USER = True