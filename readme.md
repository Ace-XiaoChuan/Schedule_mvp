## 写在前面
本项目旨在通过Tkinfer来处理view，使用sqlite3来处理数据库，以后可能还会接入scikit-learn什么的机器学习、智能分类的小玩具，算是看到什么好玩就集成什么吧
主要作用是让我用电脑时能知道自己一天都做了什么，用了多久，不具有什么特殊的意义，纯粹玩票之作

## 关于版本
详细的版本更新见CHANGELOG.MD
- ✅ **0.x.x** - 已完成统计时间功能
- ✅ **1.0.x** - 已集成机器学习功能
- 🚧 **1.1.x** - 加入随机森林(待完成)

## 项目结构

schedule_mvp/
├─ main
├─ database
├─ models
├─ view
├─ ai/
│  ├─ ai_classifier
│  ├─ tasks.csv
│  ├─ simple_model.pkl