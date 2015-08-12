#配置LDAP登录

## 配置文件：

LDAP配置文件在eoncloud_web/local/ladp_settings.py:

Example：
```python
	#-*- coding=utf-8 -*-
    import ldap
    from django_auth_ldap.config import LDAPSearch
    
    # Baseline configuration.
    AUTH_LDAP_SERVER_URI = "ldap://127.0.0.1:389/"
    
    AUTH_LDAP_BIND_DN = "uid=admin,ou=system"
    AUTH_LDAP_BIND_PASSWORD = "12345"
    
    AUTH_LDAP_USER_SEARCH = LDAPSearch("ou=users,dc=example,dc=com",
                                       ldap.SCOPE_SUBTREE, "(cn=%(user)s)")
    # or perhaps:
    # AUTH_LDAP_USER_DN_TEMPLATE = "uid=%(user)s,ou=users,dc=eoncloud,dc=com"
    
    AUTH_LDAP_USER_ATTR_MAP = {
        "first_name": "givenName",
        "last_name": "sn",
        "email": "mail"
    }
    
    AUTH_LDAP_ALWAYS_UPDATE_USER = True

    ＃Group related configuration
    # AUTH_LDAP_GROUP_TYPE = GroupOfNamesType(name_attr='cn')

    # AUTH_LDAP_FIND_GROUP_PERMS = True
    # AUTH_LDAP_MIRROR_GROUPS = True

    # AUTH_LDAP_GROUP_SEARCH = LDAPSearch("ou=groups,dc=bluven,dc=me",
    #                                     ldap.SCOPE_SUBTREE,
    #                                     (objectClass=groupOfNames)")
    
    # Simple group restrictions
    # AUTH_LDAP_REQUIRE_GROUP = "ou=system"
    # AUTH_LDAP_DENY_GROUP = "ou=system"
    
    # Cache group memberships for an hour to minimize LDAP traffic
    #AUTH_LDAP_CACHE_GROUPS = False
    #AUTH_LDAP_GROUP_CACHE_TIMEOUT = 3600
```

该配置文件主要有２部分配置：　用户配置，组配置．用户配置是必须的，组配置是可选的，默认情况下组配置是注释掉的．

## LDAP用户验证基本原理

每个用户在LDAP系统中有一个唯一的DN值，例如配置文件中默认的admin用户在LDAP中的DN值是`uid=admin,ou=system,dc=eoncloud,dc=com`, 其中eoncloud.com是域名，system是组名，admin是用户名，有些LDAP用cn而不是uid来生成DN，在这种系统中admin的DN看起来像这样`cn=admin,ou=system,dc=eoncloud,dc=com`，无论是uid还是cn或是别的前缀，django-ldap-auth都是用dn来验证用户和获取用户信息的.

假设用户输入的帐号及密码是：　test, password.

django-auth-ldap有２个方式来获取用户的DN

 1. 使用`AUTH_LDAP_USER_DN_TEMPLATE`提供的模板生成DN．如`uid=%(user)s,ou=users,dc=eoncloud,dc=com`,
    其中%(user)s会被替换成用户名，这样最终的DN就是`uid=test,ou=users,dc=eonclooud,dc=com`.
 2. 使用`AUTH_LDAP_GROUP_SEARCH`．如果没有配置`AUTH_LDAP_USER_DN_TEMPLATE`，那么django-auth-ldap会使用`AUTH_LDAP_BIND_DN`和`AUTH_LDAP_BIND_PASSWORD`提供的dn与密码根据`AUTH_LDAP_GROUP_SEARCH`提供的查询条件去查找test用户，如果查不到，验证失败，如果查到用户，就使用返回的数据生成test的DN.　
 3. 利用第2步生成DN值与密码尝试访问LDAP系统，如果访问成功，则验证共过，否则验证失败．

## 基本配置

1. AUTH_LDAP_SERVER_URI． LDAP系统的地址及端口号
2. AUTH_LDAP_BIND_DN, AUTH_LDAP_BIND_PASSWORD. 查找用户及相关信息的默认用户信息
3. AUTH_LDAP_USER_SEARCH．　第一个参数指指定询目录，第三个参数是过滤条件，过滤条件可以很复杂，有需要请查看相关文档．
4. AUTH_LDAP_USER_DN_TEMPLATE．　用户DN模板，配置该参数后django-auth-ldap会用生成的DN配合密码验证该用户．
5. AUTH_LDAP_USER_ATTR_MAP.　LDAP与User model映射．
6. AUTH_LDAP_ALWAYS_UPDATE_USER.　是否同步LDAP修改．

## 用户组配置

如果需要，django-auth-ldap可以从ldap系统获取用户的组信息，也可以限定某个组里的用户访问，或者阻止某个组里的用户访问，无论是使用哪个功能都需要先配置组类型`AUTH_LDAP_GROUP_TYPE`及`AUTH_LDAP_GROUP_SEARCH`,　因为LDAP里组的种类非常多，具体信息请查询相关资料．

`AUTH_LDAP_GROUP_TYPE`
   
 - 值类型: LDAPGroupType的子类实例．LDAPGroupType有２个初始化参数:member_attr, name_attr．member_attr是组成员的属性名, name_attr是组名称的属性名．
 - 作用:　AUTH_LDAP_GROUP_SEARCH返回的组的类型，并用来判断用户与组的从属关系

`AUTH_LDAP_GROUP_SEARCH`
   
 - 值类型: LDAPSearch实例．
 - 作用:　用户组的查询条件

`AUTH_LDAP_REQUIRE_GROUP`

 - 值类型: 组的DN
 - 作用: 只有指定组的用户可以访问

    
`AUTH_LDAP_DENY_GROUP`指定的
    

 - 值类型: 组的DN
 - 作用：　禁止指定组的用户访问

    
`AUTH_LDAP_MIRROR_GROUPS`

 - 值类型: bool值 
 - 作用: 导入用户的组信息

## django-auth-ldap 与　Active Directory

微软的Active Directory与其他的LDAP实现有些不同，其登录不是用DN而是principalName，推荐配置django-auth-ldap时使用`AUTH_LDAP_USER_DN_TEMPLATE`,例子如下：

```python
    # Baseline configuration.
    AUTH_LDAP_SERVER_URI = "ldap://127.0.0.1:389/"
    
    AUTH_LDAP_BIND_DN = "administrator@eoncloud.com"
    AUTH_LDAP_BIND_PASSWORD = "123456."
    AUTH_LDAP_USER_SEARCH = LDAPSearch("cn=Users,dc=project,dc=com",
                                       ldap.SCOPE_SUBTREE,
                                       "(userPrincipalName=%(user)s)")
    
    AUTH_LDAP_USER_DN_TEMPLATE = '%(user)s'
    
    AUTH_LDAP_USER_ATTR_MAP = {
        "first_name": "givenName",
        "last_name": "sn",
        "email": "mail"
    }
    
    # 是否允许更新ladp用户
    AUTH_LDAP_ALWAYS_UPDATE_USER = False
```
