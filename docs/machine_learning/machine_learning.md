# 机器学习

机器学习是一个使计算机能够在没有明确编程的情况下学习的研究领域。
(field of study that gives computers the ability to learn without being explicitly programmed.)

-- by Arthur Samuel

一般来说，训练的次数越多，效果越好。

## 监督式机器学习 (supervised learning)：回归和分类
监督式机器学习，或更常见的说法，监督式学习，是指学习 x 到 y 或输入到输出映射的算法。
监督学习的关键特征是，给学习算法一些示例来学习。例子中包括正确的答案，即给定输入x时，会获得正确标签y，
并且通过看到正确的输入值x对和期望的输出标签y，学习算法最终学会只接受输入而不带输出标签，并给出相当准确的输出预测或猜测值。
更多关于监督式学习的内容请参考：[监督式机器学习](supervised_learning/introduction.md)

监督式学习主要分为两类，回归 (regression) 和分类 (classification)。
在回归中，学习算法会在无限多的可能数字输出中做出预测；在分类中，学习算法会在一个小集合中 (包含了所有可能输出的一个集合) 做出预测。

## 非监督式机器学习 (unsupervised learning)
监督式学习是从被标记了"正确答案"的数据中学习；而非监督式学习则是直接从未标记的数据中寻找有趣的东西。
在无监督学习中，数据仅带有输入X，而没有输出标签Y，并且算法必须在数据中找到某种结构或某种模式或有趣的东西。

例如：
* Clustering: 将相似的数据放在一起，例如新闻热搜。

* Anomaly detection: 寻找不一样的新闻点。

* Dimensionality reduction: 压缩数据 (使用更少的数字)。
