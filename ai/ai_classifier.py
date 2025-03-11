import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
from pathlib import Path
import jieba
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns


# joblib 是一个用于 简化并行计算 和 高效序列化大型数据 的 Python 库。
# 自定义中文分词器
def chinese_tokenizer(text):
    # 全局函数
    return jieba.lcut(text)


class SimpleClassifier:
    def __init__(self, max_features=5000, n_estimators=100):
        self.script_dir = Path(__file__).parent
        self.data_path = self.script_dir / "tasks.csv"
        self.model_path = self.script_dir / "simple_model.pkl"
        # 调试路径（完成后可删除）
        print(f"数据路径：{self.data_path}")
        print(f"模型路径：{self.model_path}")

        # model是训练好的分类器
        # Pipeline接受一个列表，每个tuple都是一个二元组（name, operation）
        self.model = Pipeline([
            # TfidfVectorizer() 会将输入的文本数据转换成数值化的特征矩阵，每个单词的权重由其在文本中的频率和逆文档频率决定。
            ('tfidf', TfidfVectorizer(
                ngram_range=(1, 2),
                tokenizer=chinese_tokenizer,  # 添加自定义分词器
                token_pattern=None,  # 禁用默认正则分词
                max_features=5000,  # 特征维度
                stop_words=["的", "了", "在", "于", "与", "是"]
            )),
            # 第二个步骤：分类器。
            ('clf', RandomForestClassifier(
                n_estimators=100,  # 树的数量
                class_weight='balanced',
                random_state=42  # 确保结果可复现
            ))  # 分类器
            # 元组中的第一个元素是该步骤的名称，第二个元素是转换器/估计器
        ])

    def train(self):
        data = pd.read_csv(self.data_path)
        # 新增，打乱数据顺序
        data = data.sample(frac=1).reset_index(drop=True)
        print(f"成功加载{len(data)}条真实样本数据")
        self.model.fit(data['text'], data['label'])
        joblib.dump(self.model, self.model_path)

    def predict(self, text):
        """
        返回预测结果，于main里被调用
        :param text: text = self.view.title_entry.get()
        :return: 预测结果及预测准确率
        """
        # 老忘，这个model跟mvc的那个重名了，但是实际意思是上边构造函数训练好的分类器
        # 另外关于predict([text])[0]：[text]将单个文本字符串包装成列表，因为scikit-learn的predict方法通常期望一个样本集合，即使只有一个样本也需要列表形式。
        pred = self.model.predict([text])[0]

        # 我的方法：
        # 决策分数（即样本至超平面的距离）
        # decision_score = self.model.decision_function([text])[0]
        # # 计算置信度百分比（基于决策分数相对值）
        # max_score = np.max(decision_score)
        # min_score = np.min(decision_score)
        # confidence = int(100 * (max_score - min_score) / (max_score if max_score != 0 else 1))
        # return pred, min(100, max(0, confidence))  # 确保在0-100之间

        # 新方法：
        # decision_scores = self.model.decision_function([text])[0]
        # exp_scores = np.exp(decision_scores - np.max(decision_scores))
        # probs = exp_scores / exp_scores.sum()
        # confidence = int(100 * probs.max())
        # return pred, confidence

        # 随机森林内置的概率估计方法：
        probs = self.model.predict_proba([text])[0]
        confidence = int(100 * np.max(probs))
        return pred, confidence

    #         对于新的方法，感觉在重点不在编程上，在数学上。举个例子：decision_scores=[5,3,2],然后减去当中的最大值→[[0, -2, -3]（以免指数爆炸）
    #         exp为指数运算，计算结果为[1.0, 0.135, 0.050]，经过这样的计算，全部转化为正数，并且放大了之间的差异。这是L80做的事情。
    #         然后将指数值除总和，得到了概率分布，例如：1.0 + 0.135 + 0.050 = 1.185 → 概率为 [0.844, 0.114, 0.042]，再取最大的转为百分比，
    #         这种计算方式被称作softmax
    def evaluate(self):
        """
        生成、显示混淆矩阵
        """
        # 先加载数据
        data = pd.read_csv(self.data_path)

        # 划分训练测试集
        X_train, X_test, y_train, y_test = train_test_split(
            data['text'], data['label'],
            test_size=0.2,
            random_state=42
        )

        # - 如果已有模型：加载
        # - 如果没有模型：训练
        if Path(self.model_path).exists():
            self.model = joblib.load(self.model_path)  # 加载已保存的模型
        else:
            self.model.fit(X_train, y_train)  # 训练新模型
            joblib.dump(self.model, self.model_path)  # 保存模型

        # 预测测试集
        y_pred = self.model.predict(X_test)

        # 生成混淆矩阵
        cm = confusion_matrix(y_test, y_pred)

        # 可视化
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm,
                    annot=True,
                    fmt='d',
                    cmap='Blues',
                    xticklabels=['工作', '休闲', '睡眠'],
                    yticklabels=['工作', '休闲', '睡眠'])
        plt.title('Confusion Matrix')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.show()


if __name__ == "__main__":
    classifier = SimpleClassifier()
    classifier.train()  # 新增训练步骤
    print(classifier.predict("学习Python"))
