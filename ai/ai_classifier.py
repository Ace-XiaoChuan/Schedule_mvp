import logging
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
from core import config

logger = logging.getLogger('schedule_mvp')


def chinese_tokenizer(text):
    # 全局函数
    return jieba.lcut(text)


class SimpleClassifier:
    def __init__(self, max_features=5000, n_estimators=100):
        self.script_dir = Path(__file__).parent  # ai
        self.data_path = config.config.DATA_PATH
        self.model_path = config.config.MODEL_DIR
        logger.debug(f"模型数据为：{self.data_path}")
        logger.debug(f"数据路径为：{self.model_path}")

        # model是训练好的分类器
        # Pipeline接受一个列表，每个tuple都是一个二元组（name, operation）
        self.model = Pipeline([
            # TfidfVectorizer() 会将输入的文本数据转换成数值化的特征矩阵，每个单词的权重由其在文本中的频率和逆文档频率决定。
            ('tfidf', TfidfVectorizer(
                ngram_range=(1, 2),  # 提取文本中的词或短语的长度范围,(1, 2)：提取单个词和相邻两个词的上下文关系
                tokenizer=chinese_tokenizer,  # 添加自定义分词器
                token_pattern=None,  # 禁用默认正则分词
                max_features=2000,  # 特征维度
                stop_words=["的", "了", "在", "于", "与", "是", "我"]
            )),
            # 第二个步骤：分类器。
            ('clf', RandomForestClassifier(
                n_estimators=70,  # 树的数量
                max_depth=5,#树太深会过拟合
                min_samples_split=10,  # 增加分裂最小样本数
                class_weight='balanced',
                random_state=42  # 确保结果可复现
            ))  # 分类器
            # 元组中的第一个元素是该步骤的名称，第二个元素是转换器/估计器
        ])

    def train(self):
        data = pd.read_csv(self.data_path)

        # 打乱数据顺序，.sample()会抽样，frac=1即抽取100%的样本
        data = data.sample(frac=1).reset_index(drop=True)
        logger.info(f"成功加载{len(data)}条真实样本数据")
        self.model.fit(data['text'], data['label'])  # 开始训练
        joblib.dump(self.model, self.model_path)

    def predict(self, text):
        """返回预测结果，于main里被调用，这套技术栈predict使用Pipeline原生计算，BERT就调用BERT原生
        :param text: text = self.view.title_entry.get()
        :return: 预测结果(str)及预测准确率：array（[30%,20%,10%]）
        """
        # 这里model是上边构造函数训练好的分类器模型
        # self.model.predict([text]) 返回一个列表,第一个元素为最可能结果
        pred: str = self.model.predict([text])[0]

        # predict_proba([text])返回二维数组，probs=predict_proba([text])[0]返回一维NumPy数组
        # nd:n-dimensional
        probs: np.ndarray = self.model.predict_proba([text])[0]
        confidence = int(100 * np.max(probs))
        return pred, confidence

    def evaluate(self):
        """
        生成、显示混淆矩阵
        """

        # 先加载数据
        data = pd.read_csv(self.data_path)
        labels: list = sorted(data['label'].unique())

        print("数据分布统计:")
        print(data['label'].value_counts())  # 3

        # 划分训练测试集、分层抽样
        # x_train 和 y_train：训练集中的特征数据和对应的标签，eg:吃饭睡觉打豆豆，休闲
        # x_test 和 y_test：测试集中的特征数据和对应的标签数据
        x_train, x_test, y_train, y_test = train_test_split(
            data['text'], data['label'],
            test_size=0.4,  # 训练集测试集6:4吧，以后如果引入验证集，那就6:2:2
            stratify=data['label'],
            random_state=42
        )

        # 如果已有模型：加载
        if Path(self.model_path).exists():
            self.model = joblib.load(self.model_path)  # 加载已保存的模型
        # 如果没有模型：用训练集数据训练
        else:
            logger.error("未检测到训练模型，开始进行全量训练...")
            self.model.fit(x_train, y_train)  # 训练新模型
            joblib.dump(self.model, self.model_path)  # 保存模型

        # 预测测试集
        y_pred = self.model.predict(x_test)

        # 生成混淆矩阵
        cm = confusion_matrix(y_test, y_pred)

        # 计算百分比，进行归一化，cm.sum(axis=1)按行求和，axis=1表示行方向
        # np.newaxis 的作用是增加一个维度，将一维数组转换为二维列向量
        cm_percent = cm / cm.sum(axis=1)[:, np.newaxis]

        # 可视化:创建窗口
        plt.figure(figsize=(8, 6), dpi=120)

        # 组合数值和百分比
        annot = []
        for i in range(len(cm)):
            for j in range(len(cm)):
                percent = cm_percent[i, j]
                color = "white" if percent > 0.5 else "black"  # 自适应文字颜色
                plt.text(j + 0.5, i + 0.5,
                         f"{cm[i, j]}\n({percent:.1%})",
                         ha="center", va="center",
                         color=color)

        # seaborn热力图
        sns.heatmap(cm,
                    annot=[[f"{val}\n({perc:.1%})" for val, perc in zip(cm_row, percent_row)]
                           for cm_row, percent_row in zip(cm, cm_percent)],
                    fmt='',
                    cmap='Blues',
                    xticklabels=labels,
                    yticklabels=labels
                    )
        plt.title('混淆矩阵（Confusion Matrix）')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.show()


if __name__ == "__main__":
    classifier = SimpleClassifier()
    classifier.train()  # 新增训练步骤
    print(classifier.predict("学习Python"))
