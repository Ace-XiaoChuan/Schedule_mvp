import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
import joblib
from pathlib import Path
import jieba
from sklearn.ensemble import RandomForestClassifier


# joblib 是一个用于 简化并行计算 和 高效序列化大型数据 的 Python 库。
# 自定义中文分词器
def chinese_tokenizer(text):
    # 这是模块级别的普通函数，所以没有self，也就是全局函数
    return jieba.lcut(text)


class SimpleClassifier:
    def __init__(self):
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
            # TfidfVectorizer() 会将输入的文本数据转换成数值化的特征矩阵，每个单词的权重由其在文本中的频率和逆文档频率决定。
            ('tfidf', TfidfVectorizer(
                tokenizer=chinese_tokenizer,  # 添加自定义分词器
                token_pattern=None,  # 禁用默认正则分词
                max_features=5000,  # 优化特征维度
                stop_words=["的", "了", "在", "于", "与", "是"]
            )),
            # 第二个步骤：分类器。
            # LinearSVC 是 scikit-learn 中的一个分类器，属于支持向量机（SVM）的一种实现。它用于进行线性分类，
            # 通过寻找一个超平面将不同类别的数据进行区分。这个步骤会使用从 TfidfVectorizer 输出的特征（TF-IDF 特征矩阵）来训练一个分类模型。
            # SVM 的核心思想是通过找到一个最佳的超平面（decision hyperplane）来分离不同类别的数据。
            # 它在机器学习中非常流行，尤其是在小样本、特征较高的情境中表现出色。最优超平面的选择标准是使得两类数据点之间的间隔最大化，
            # 每个数据点都要满足它位于正确的类别一侧，即离超平面正确的一侧
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
        probs=self.model.predict_proba([text])[0]
        confidence = int(100 * probs())
        return pred, confidence


#         对于新的方法，感觉在重点不在编程上，在数学上。举个例子：decision_scores=[5,3,2],然后减去当中的最大值→[[0, -2, -3]（以免指数爆炸）
#         exp为指数运算，计算结果为[1.0, 0.135, 0.050]，经过这样的计算，全部转化为正数，并且放大了之间的差异。这是L80做的事情。
#         然后将指数值除总和，得到了概率分布，例如：1.0 + 0.135 + 0.050 = 1.185 → 概率为 [0.844, 0.114, 0.042]，再取最大的转为百分比，
#         这种计算方式被称作softmax


if __name__ == "__main__":
    classifier = SimpleClassifier()
    classifier.train()  # 新增训练步骤
    print(classifier.predict("学习Python"))
