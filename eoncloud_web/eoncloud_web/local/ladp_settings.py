#-*- coding=utf-8 -*-
import ldap
from django_auth_ldap.config import LDAPSearch, GroupOfNamesType


# Baseline configuration.
AUTH_LDAP_SERVER_URI = "ldap://localhost:10389/ou=system"

AUTH_LDAP_BIND_DN = "uid=admin,ou=system"
AUTH_LDAP_BIND_PASSWORD = "123456"
AUTH_LDAP_USER_SEARCH = LDAPSearch("ou=system",
                                   ldap.SCOPE_SUBTREE, "(uid=%(user)s)")
# or perhaps:
# AUTH_LDAP_USER_DN_TEMPLATE = "uid=%(user)s,ou=users,dc=example,dc=com"

# 用户所属用户组搜索路径.
AUTH_LDAP_GROUP_SEARCH = LDAPSearch("ou=system",
                                    ldap.SCOPE_SUBTREE, "(objectClass=groupOfNames)"
                                    )
AUTH_LDAP_GROUP_TYPE = GroupOfNamesType(name_attr="ou")

# # Simple group restrictions
# AUTH_LDAP_REQUIRE_GROUP = "ou=system"
# AUTH_LDAP_DENY_GROUP = "ou=system"

# 定义本地django用户和ladp用户映射.
AUTH_LDAP_USER_ATTR_MAP = {
    "first_name": "givenName",
    "last_name": "sn",
    "email": "mail"
}



# 是否允许更新ladp用户
#AUTH_LDAP_ALWAYS_UPDATE_USER = False

# 查找组权限
#AUTH_LDAP_FIND_GROUP_PERMS = True

# Cache group memberships for an hour to minimize LDAP traffic
#AUTH_LDAP_CACHE_GROUPS = False
#AUTH_LDAP_GROUP_CACHE_TIMEOUT = 3600



AUTHENTICATION_BACKENDS = (
    'django_auth_ldap.backend.LDAPBackend',
)