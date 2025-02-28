## [0.0.1] - 2025-02-14
### Added
- 新增功能：创建了mvp版本的main.py，并添加了一个测试数据，测试可以正常使用
- 新增功能：初始化数据库

## [0.0.2] - 2025-02-16
### Changed
- 迭代了database.py和main.py的部分代码，使之可以使用tk模块交互
### Added
- 增加了.gitignore作为版本控制

## [0.0.3] - 2025-02-17
### Changed
- 	更改了database.py的部分配置，使之适配未来需要的时间分类功能

## [0.0.4] - 2025-02-19
### Added
- 新增功能：完成了mvp版本预计的全部内容，包括自动与手动记录时间、任务工作分类计时等内容
### Changed
- 在deepseek的指导下开始着手进行按照mvc的重构，但是效果不理想

## [0.1.1] - 2025-02-21
### Deprecated
- 废弃功能：放弃了d指导的一步到位mvc重构，冲击太大了，暂时先完成了models的重构，并测试无误

## [0.1.2] - 2025-02-22
### Added
- 新增功能：完成了view视图的处理，并将main函数作为控制器，测试可以正常使用，这宣告mcv重构顺利完成

## [1.0.0] - 2025-02-24
### Added
- 新增功能：新增ai预测类别功能的mvp版本，但预测结果根本不准，仍需进一步优化

## [1.0.1] - 2025-02-25
### Fixed
- 修正代码：完善了逻辑，取消了一部分硬编码
- 修正代码：改正了database.py中SQL的插入表格语法错误

## [1.0.2] - 2025-02-26
### Added
- 新增功能：新增ai预测类别功能的置信度提示，但是暂时还无法再view里显示，等待后续更新吧

## [1.0.3] - 2025-02-27
### Fixed
- [1.0.3.a]重构了一部分代码，代码量已经有点大了，对于我这样的新手阅读都有点费劲了，或许我应该在d指导的帮助下进行分层架构的重构
- [1.0.3.b]在d指导的帮助下，在分层架构的设计原则下，尝试实践依赖注入和职责转移的设计思想
- 依赖注入 关注的是如何将对象所依赖的外部资源由外部传入，从而实现模块间的解耦与可测试性提高。
- 职责转移 则是将某个模块的部分职责交给其他更专门的模块来处理，从而实现关注点分离和系统整体的模块化设计。
- 下图是从mcv转为分层设计后的序列图，可以看到虽然模块变多了，但是逻辑清楚了不少

```mermaid
sequenceDiagram
    participant User as 用户
    participant View as 视图层 (view.py)
    participant Controller as 控制器 (main.py)
    participant Model as 模型层 (models.py)
    participant Database as 数据库

    User->>View: 1. 填写表单并点击"添加手动任务"
    activate View
    View->>Controller: 2. 触发 handle_manual_task()
    activate Controller

    Controller->>View: 3. 调用 get_manual_task_data()
    activate View
    View-->>Controller: 返回表单数据 {title, category, ...}
    deactivate View

    Controller->>Controller: 4. 直接验证数据（无服务层）
    Note over Controller: 控制器承担业务逻辑
    
    Controller->>Model: 5. 调用 add_manual_task()
    activate Model
    Model->>Database: 6. 执行原始SQL插入
    activate Database
    Database-->>Model: 返回操作结果
    deactivate Database
    Model-->>Controller: 返回任务ID
    deactivate Model

    alt 成功
        Controller->>View: 7. 调用 clear_manual_inputs()
        activate View
        View-->>User: 清空表单
        deactivate View
        Controller->>View: 8. 调用 refresh_task_list()
        View->>Model: 9. 调用 get_all_tasks()
        Model->>Database: 10. 查询所有任务
        Database-->>Model: 返回数据
        Model-->>View: 返回任务列表
        View-->>User: 刷新任务列表显示
    else 失败
        Controller->>View: 7. 调用 show_error()
        View-->>User: 显示错误弹窗
    end
    deactivate Controller
    deactivate View
```

```mermaid
sequenceDiagram
    participant View as 视图层 (view.py)
    participant Controller as 控制器 (main.py)
    participant Service as 服务层 (services/task_service.py)
    participant Repository as 仓储层 (repositories/task_repository.py)
    participant DB as 数据库

    View->>Controller: 用户点击"添加手动任务"按钮
    Controller->>View: 调用get_manual_task_data()获取表单数据
    View->>Controller: 返回表单数据字典
    Controller->>Service: 调用create_manual_task(data)
    Service->>Service: 1. 数据验证
    Service->>Service: 2. AI分类校验
    Service->>Repository: 3. 调用add_task()
    Repository->>DB: 执行SQL插入操作
    DB->>Repository: 返回新任务ID
    Repository->>Service: 返回存储结果
    Service->>Controller: 返回操作状态
    Controller->>View: 调用clear_inputs()/show_error()
```

```mermaid
flowchart TB
    重构前[重构前代码结构] -->|提取服务层| 重构后[重构后代码结构]
    
    subgraph 重构前
        A[Controller]
        A --> B[直接操作Model]
        A --> C[直接处理业务逻辑]
    end
    
    subgraph 重构后
        D[Controller] --> E[调用Service]
        E[Service] --> F[操作Model]
        E --> G[使用Repository]
    end
```
## [1.0.4] - 2025-02-28
### Deprecated
- 还原回了1.0.2，浪费了不少精力，但是实在是理不清方法之间的依赖关系了，之前的UML也白做了
### Fixed
- 转而重构了以下内容,可以看到是重构了，但是只重构了一点点，下一次更新应该关注于控制器，控制器已经有点尾大不掉了
```mermaid
sequenceDiagram
    participant View
    participant Controller
    participant Model
    participant Database
    
    View->>Controller: 点击"停止任务"
    Controller->>Controller: 生成 end_time
    Controller->>Model: add_task({title,category,start_time,end_time,is_auto=1})
    Model->>Database: INSERT INTO tasks(...)
    Database-->>Model: 返回新任务ID(cursor)
    Model-->>Controller: 操作结果
    Controller->>View: refresh_task_list()
    View->>Model: get_all_tasks()
    Model->>Database: SELECT * FROM tasks
    Database-->>View: 返回任务数据
    View-->>User: 显示更新后的列表
```
---

除了 Added（新增）和 Changed（变更）之外，常见的记录类型还有：

Deprecated（弃用）
表示某些功能或特性不推荐使用了，可能会在未来版本中移除。

Removed（移除）
表示某些功能或特性已被删除。

Fixed（修复）
用于记录修复的 bug 或问题。

Security（安全）
表示修复了安全漏洞或对安全相关的改进。