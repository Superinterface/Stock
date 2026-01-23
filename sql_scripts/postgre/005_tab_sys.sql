-- 1. 用户表
CREATE TABLE sys_user (
    id varchar(32),
    username VARCHAR(50) UNIQUE NOT NULL,    -- 登录账号
    password_hash VARCHAR(255) NOT NULL,     -- 密码哈希
    real_name VARCHAR(50),                  -- 真实姓名
    is_active INTEGER,         -- 是否启用
    create_time TIMESTAMP DEFAULT NOW()
);
COMMENT ON TABLE sys_user IS '系统用户表';

-- 2. 角色表
CREATE TABLE sys_role (
    id varchar(32),
    role_name VARCHAR(50) UNIQUE NOT NULL,   -- 角色标识 (如: admin, researcher)
    role_desc VARCHAR(100),                 -- 角色描述
    create_time TIMESTAMP DEFAULT NOW()
);
COMMENT ON TABLE sys_role IS '角色定义表';

-- 3. 用户-角色关联表 (多对多)
CREATE TABLE sys_user_role (
    user_id varchar(32),
    role_id varchar(32),
    PRIMARY KEY (user_id, role_id)
);
COMMENT ON TABLE sys_user_role IS '用户与角色的多对多关联表';

-- 4. 菜单/权限表
CREATE TABLE sys_menu (
    id varchar(32) PRIMARY KEY,
    parent_id varchar(32),            -- 父菜单ID (用于树形结构)
    menu_name VARCHAR(50) NOT NULL,          -- 菜单名称 (如: 股票行情)
    menu_type VARCHAR(20),                  -- 类型: M目录, C菜单, F按钮/接口
    path VARCHAR(100),                      -- 前端路由路径/接口路径
    perms VARCHAR(100),                     -- 权限标识 (如: stock:list, stock:export)
    order_num INTEGER DEFAULT 0,            -- 显示排序
    create_time TIMESTAMP DEFAULT NOW()
);
COMMENT ON TABLE sys_menu IS '系统菜单权限表';

-- 5. 角色-菜单授权表 (多对多)
CREATE TABLE sys_role_menu (
    role_id varchar(32),
    menu_id varchar(32),
    PRIMARY KEY (role_id, menu_id)
);
COMMENT ON TABLE sys_role_menu IS '角色与菜单权限的关联表';