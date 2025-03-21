import numpy as np
import pandas as pd
import torch
from transformers import BertTokenizer, BertForSequenceClassification, AdamW
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from core import config
from core.logger import configure_logger
import logging

logger = logging.getLogger('schedule_mvp')  # getLogger()可以实现全局共享、单例模式，真的好方便


class SimpleClassifier:
    def __init__(self, max_features=5000, n_estimators=100):  # 参数保留但不使用，仅为兼容
        self.script_dir = Path(__file__).parent  # ai
        self.data_path = config.config.DATA_PATH  # tasks.csv路径
        self.model_path = config.config.MODEL_DIR  # 模型保存路径
        logger.debug(f"模型数据为：{self.data_path}")
        logger.debug(f"数据路径为：{self.model_path}")

        # 初始化了一个 BERT 分词器（tokenizer）。
        # from_pretrained('bert-base-chinese') 表示从预训练模型 'bert-base-chinese' 中加载分词器。
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-chinese')

        # BertForSequenceClassification 是 Hugging Face 提供的一个 BERT 变体，专门用于分类任务，比如判断一段文本属于哪个类别。
        # self.model 是这个模型的实例，后续会用来对文本进行分类预测。
        self.model = BertForSequenceClassification.from_pretrained(
            'bert-base-chinese',
            num_labels=3  # 分类数：工作、休闲、睡眠
        )

        # 创建一个字典和反向映射字典。反向映射字典：将数字标签转换回中文标签，使用字典推导式，比较优雅
        self.label_map = {"工作": 0, "休闲": 1, "睡眠": 2}
        self.inverse_label_map = {v: k for k, v in self.label_map.items()}
        # 检测并选择模型运行的设备（GPU 或 CPU）
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # 将模型移动到指定的设备上
        self.model.to(self.device)

    def train(self):
        """训练BERT模型并保存"""
        # 加载数据
        data = pd.read_csv(self.data_path)
        data = data.sample(frac=1).reset_index(drop=True)  # 打乱数据
        logger.info(f"成功加载{len(data)}条真实样本数据")

        # 数据预处理
        texts = data['text'].tolist()
        labels = [self.label_map[label] for label in data['label']]
        encodings = self.tokenizer(texts, padding=True, truncation=True, max_length=32, return_tensors="pt")
        dataset = TensorDataset(
            encodings['input_ids'],
            encodings['attention_mask'],
            torch.tensor(labels)
        )
        dataloader = DataLoader(dataset, batch_size=16, shuffle=True)

        # 优化器
        optimizer = AdamW(self.model.parameters(), lr=2e-5)

        # 训练循环
        self.model.train()
        for epoch in range(3):  # 训练3轮
            for batch in dataloader:
                input_ids, attention_mask, labels = [b.to(self.device) for b in batch]
                outputs = self.model(input_ids, attention_mask=attention_mask, labels=labels)
                loss = outputs.loss
                loss.backward()
                optimizer.step()
                optimizer.zero_grad()
            logger.info(f"Epoch {epoch + 1} 完成，损失: {loss.item():.4f}")

        # 保存模型
        self.model.save_pretrained(self.model_path)
        self.tokenizer.save_pretrained(self.model_path)
        logger.info("模型训练完成并保存")

    def predict(self, text):
        """预测单个任务标题的分类"""
        self.model.eval()
        inputs = self.tokenizer(text, padding=True, truncation=True, max_length=32, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model(**inputs)
        logits = outputs.logits
        pred_idx = torch.argmax(logits, dim=1).item()
        confidence = torch.softmax(logits, dim=1).max().item() * 100

        pred_category = self.inverse_label_map[pred_idx]
        return pred_category, int(confidence)

    def evaluate(self):
        """生成并显示混淆矩阵"""
        data = pd.read_csv(self.data_path)
        labels = sorted(self.label_map.keys())

        # 划分训练和测试集
        x_train, x_test, y_train, y_test = train_test_split(
            data['text'], data['label'],
            test_size=0.2,
            stratify=data['label'],
            random_state=42
        )
        logger.info("数据分布统计:")
        logger.info(data['label'].value_counts())

        # 检查是否已有训练模型
        model_dir = Path(self.model_path)
        if model_dir.exists() and any(model_dir.iterdir()):
            self.model = BertForSequenceClassification.from_pretrained(self.model_path)
            self.tokenizer = BertTokenizer.from_pretrained(self.model_path)
            logger.info("加载已有模型")
        else:
            logger.error("未检测到训练模型，开始全量训练...")
            self.train()

        # 预测测试集
        self.model.to(self.device)
        self.model.eval()
        y_pred = []
        for text in x_test:
            pred, _ = self.predict(text)
            y_pred.append(self.label_map[pred])

        # 生成混淆矩阵
        y_test_numeric = [self.label_map[label] for label in y_test]
        cm = confusion_matrix(y_test_numeric, y_pred)
        cm_percent = cm / cm.sum(axis=1)[:, np.newaxis]

        # 可视化
        plt.figure(figsize=(8, 6), dpi=120)
        sns.heatmap(
            cm,
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
    classifier.train()
    pred, conf = classifier.predict("学习Python")
    print(f"预测分类: {pred}, 置信度: {conf}%")
