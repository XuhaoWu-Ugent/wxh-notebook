# 梯度, 散度, 旋度

## 偏微分 (Partial Differentiation)

Scalar quantity $f$, which is a function of three variables, so $f=f(x, y, z)$.
The partial derivative of $f$ with respect to $x$ is defined to be the derivative of $f$ with respect to $x$, regarding $y$ and $z$ as constants. 
To indicate that $f$ is a function of move than ore variable, the partial derivative is written using a curly $d, \partial$.

The partial derivative of $f$ with respect to $x$ is defined to be the derivative of $f$ with respect to $x$, regarding $y$ and $z$ as constants.
To indicate that $f$ is a function of move than ore variable, the partial derivative is written using a curly $d, \partial$.
more formally, the definition of the partial derivative is

$$
\frac{\partial f}{\partial x}=\lim _{\delta x \rightarrow 0} \frac{f(x+\delta x, y, z)-f(x, y, z)}{\delta x}
$$

Second derivatives, such as $\partial^2 f / \partial x^2$ and mixed derivatives, such as $\partial^2 f / \partial y \partial x$ can also be defined: 
the mixed derivative means that $f$ is differentiated with respectoto $x$ regarding $y$ as a constant, and then differentiated with respect to $y$ regarding $x$ as a constant. 

An important property of this mixed derivative, or cross-derinative, is that the order of the two derivatives does not matter, i.e.)

$$
\frac{\partial^2 f}{\partial y \partial x}=\frac{\partial^2 f}{\partial x \partial y}
$$

provided that these second partial derivatives exist and are continuous.
$\Rightarrow$ One application: When a function is at a maximum or a minimum, all of its partial derivatives are zero.

## 泰勒级数 (Taylor series)

