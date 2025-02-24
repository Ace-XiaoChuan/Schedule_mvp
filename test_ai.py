from ai.ai_classifier import SimpleClassifier

# 初始化分类器
classfier = SimpleClassifier()

# 训练测试
classfier.train('ai/tasks.csv')

# 预测测试
test_text = "我要写代码"
prediction = classfier.predict(test_text)
print(f"预测结果：'{test_text}'->{prediction}")
