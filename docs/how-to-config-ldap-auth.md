#	安装python和django相关ladp插件：

	pip install python-ldap 2.4.20
	pip install django-auth-ldap 1.2.6

#	在Django项目下添加ladp相关配置：
Example：
```python
	Import ldap
	from django_auth_ldap.config import LDAPSearch, GroupOfNamesType


	# 配置ladp服务地址
	AUTH_LDAP_SERVER_URI = "ldap://ldap.example.com"
	# 配置对应用户管理节点
	AUTH_LDAP_BIND_DN = "cn=django-agent,dc=example,dc=com"
	# 管理密码
	AUTH_LDAP_BIND_PASSWORD = "phlebotinum"
	# 验证用户搜索路径
	AUTH_LDAP_USER_SEARCH = LDAPSearch("ou=users,dc=example,dc=com",
	    ldap.SCOPE_SUBTREE, "(uid=%(user)s)")
	# 定义ladp验证用户传递模板 :
	# AUTH_LDAP_USER_DN_TEMPLATE = "uid=%(user)s,ou=users,dc=example,dc=com"

	# 用户所属用户组搜索路径.
	AUTH_LDAP_GROUP_SEARCH = LDAPSearch("ou=django,ou=groups,dc=example,dc=com",
	    ldap.SCOPE_SUBTREE, "(objectClass=groupOfNames)"
	)
	AUTH_LDAP_GROUP_TYPE = GroupOfNamesType(name_attr="cn")

	# 定义本地django用户和ladp用户映射.
	AUTH_LDAP_USER_ATTR_MAP = {
	    "first_name": "givenName",
	    "last_name": "sn",
	    "email": "mail"
	}



	# 是否允许更新ladp用户
	AUTH_LDAP_ALWAYS_UPDATE_USER = True

	# 查找组权限
	AUTH_LDAP_FIND_GROUP_PERMS = True

	# Cache group memberships for an hour to minimize LDAP traffic
	AUTH_LDAP_CACHE_GROUPS = True
	AUTH_LDAP_GROUP_CACHE_TIMEOUT = 3600


	# Keep ModelBackend around for per-user permissions and maybe a local
	# 配置django后台验证定义，但项目自定义登陆实现，此处可不配置，修改自定义登陆实现
	AUTHENTICATION_BACKENDS = (
	    'django_auth_ldap.backend.LDAPBackend',
	    'django.contrib.auth.backends.ModelBackend',
	)
```
#	修改自定义登陆方法：
	通过开关控制使用ladp验证、系统自带验证或两者均存在
	首先通过用户名去本地用户信息，调用django-ladp 验证接口，
	验证成功：
    	1. 如果本地存在用户，执行后续操作  
    	2. 如果不存在，通过验证返回信息创建本地用户，执行注册流程，创建对应openstack用户。

