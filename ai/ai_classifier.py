import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
import joblib
from pathlib import Path


# joblib 是一个用于 简化并行计算 和 高效序列化大型数据 的 Python 库。

class SimpleClassifier:
    def __init__(self):
        # 这个魔术方法用以返回当前**文件**的绝对路径,mmd
        self.script_dir = Path(__file__).parent
        self.data_path = self.script_dir / "tasks.csv"
        self.model_path = self.script_dir / "simple_model.pkl"
        # 调试路径（完成后可删除）
        print(f"数据路径：{self.data_path}")
        print(f"模型路径：{self.model_path}")

        # model是训练好的分类器
        # Pipeline 是 scikit-learn 中的一个类，用来将多个步骤（例如数据预处理、特征提取、模型训练等）
        # 串联成一个整体，使得这些步骤像一个单独的模型一样工作。它的作用是简化工作流程，并确保每个步骤都依赖于前一个步骤的输出。
        # Pipeline接受一个包含多个步骤的列表，每个步骤都是一个
        # 二元组（name, operation）
        self.model = Pipeline([
            # 第一个步骤：文本转数值（特征提取）
            # TfidfVectorizer 是 scikit-learn 提供的一个类，用于将文本数据（例如句子、文章）转换为数值特征，
            # 通常是通过 TF-IDF（Term Frequency-Inverse Document Frequency）方法来进行文本向量化。
            # TfidfVectorizer() 会将输入的文本数据转换成数值化的特征矩阵，每个单词的权重由其在文本中的频率和逆文档频率决定。
            ('tfidf', TfidfVectorizer()),
            # 第二个步骤：分类器。
            # LinearSVC 是 scikit-learn 中的一个分类器，属于支持向量机（SVM）的一种实现。它用于进行线性分类，
            # 通过寻找一个超平面将不同类别的数据进行区分。这个步骤会使用从 TfidfVectorizer 输出的特征（TF-IDF 特征矩阵）来训练一个分类模型。
            # SVM 的核心思想是通过找到一个最佳的超平面（decision hyperplane）来分离不同类别的数据。
            # 它在机器学习中非常流行，尤其是在小样本、特征较高的情境中表现出色。最优超平面的选择标准是使得两类数据点之间的间隔最大化，
            # 每个数据点都要满足它位于正确的类别一侧，即离超平面正确的一侧
            ('clf', LinearSVC())  # 分类器
        ])

    def train(self):
        data = pd.read_csv(self.data_path)
        print(f"成功加载{len(data)}条真实样本数据")
        self.model.fit(data['text'], data['label'])
        joblib.dump(self.model, self.model_path)

    def predict(self, text):
        """返回预测结果，于main里被调用"""
        # 老忘，这个model跟mvc的那个重名了，但是实际意思是上边构造函数训练好的分类器
        # 另外关于predict([text])[0]：上文说了Pipeline只返回列表，所以用[0]取数组的第一个预测结果
        pred = self.model.predict([text])[0]

        # 决策分数（即样本至超平面的距离）
        decision_score = self.model.decision_function([text])[0]

        # 计算置信度百分比（基于决策分数相对值）
        max_score = np.max(decision_score)
        min_score = np.min(decision_score)
        # 三元表达式，if max_score != 0:
        #     result = max_score
        # else:
        #     result = 1
        confidence = int(100 * (max_score - min_score) / (max_score if max_score != 0 else 1))

        return pred, min(100, max(0, confidence))  # 确保在0-100之间

if __name__ == "__main__":
    classifier = SimpleClassifier()
    classifier.train()  # 新增训练步骤
    print(classifier.predict("学习Python"))