CREATE TABLE IF NOT EXISTS `ProjectManager` (
   `companyname` char(64),
   `manager` char(64),
   `manager_status` char(64),
   `manager_level` char(128),
   `zhicheng` char(128)
)ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=0;
CREATE TABLE IF NOT EXISTS `CompanyPerformance` (
    `companyname` char(128),
    `qiyezizhi` TEXT,
    `Score` char(16),
    `Score_old` char(16),
    `types` char(16),
    `project_name` TEXT,
    `build_company` char(128),
    `gczt` char(32),
    `zbtime` char(64),
    `jgtime` char(64),
    `ystime` char(64),
    `mianji` char(64),
    `zbprice` char(64),
    `manager` char(32),
    `manager_status` char(16),
    `zhicheng` char(128),
    `shizheng_level` char(16),
    `tujian_level` char(16),
    `project_kind` char(32),
    `manager_level` char(128),
    `ocr_yszm` TEXT,
    `pic_yszm` TEXT,
    `update_time` char(32),
    CONSTRAINT uc_PerformanceID UNIQUE (companyname,project_name(128),build_company,zbtime,zbprice,manager)
    )ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=0;
CREATE TABLE IF NOT EXISTS `SpiderRunningStatus` (
   `companyname` char(64) not null,
   `info` TEXT,
   `status` char(16),
   `update_time` char(32),
   `last_succeed_time` char(32),
   primary key(companyname)
)ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=0