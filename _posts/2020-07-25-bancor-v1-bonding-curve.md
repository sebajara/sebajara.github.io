---
title: Bancor V1 bonding curve
date: 2020-07-25
tags: [Economics, Bancor, Token Bonding Curve, Fractional Reserve]
excerpt: "POST IN THE MAKING... Trading of assets can suffer from liquidity problems. Bancor proposed a protocol for ensuring liquidity by construction, using an token bonding curve and a fractional-reserve. This is being used to set the price of local community currencies. Here I overview the mathematical argument behind the V1 protocol."
mathjax: "true"
toc: true
toc_label: "Jump to:"
toc_icon: "fast-forward"
---

NOTE: this a post in the making.

TODO. General overview.

## How I got here

TODO

## Token bonding curves

TODO What is a token? 
[coinmonks](https://medium.com/coinmonks/token-bonding-curves-explained-7a9332198e0e)

If we call $$s$$ total supply or volume of tokens, a token bonding curve
$$p(...)$$ is a function that gives the value of one unit of token in
some given currency units. In such a way, if we want to buy or sell a
given amount of token we integrate $$p(...)$$ to calculate the
price. For example, say we want to buy $$x$$ amounts of token and the
current supply is $$x_0$$, then the price we pay is
$$\int_{x_0}^{x_0+x}p(...)ds$$. The interesting question is what the
price function should look like? and with what consequences?

### The liquidity problem

There are many considerations that can go into deciding a
bonding curve (e.g. see the post on the
[molecule-blog](https://medium.com/molecule-blog/token-bonding-curve-design-parameters-95d365cbec4f)).
But an obvious problem is "token
liquidity". Wikipedia
defines [market liquidity](https://en.wikipedia.org/wiki/Market_liquidity) as

> a market's feature whereby an individual or firm can quickly purchase
> or sell an asset without causing a drastic change in the asset's
> price.

With money this is not regularly a problem ("*cash is the most liquid
asset*"). But it can become one if we trade using some arbitrary
[asset](https://en.wikipedia.org/wiki/Asset). In regular markets,
liquidity is facilitated by [Market Makers](https://en.wikipedia.org/wiki/Market_maker), which

> seek to profit by charging for the immediacy of execution: either
> implicitly by earning a bid/ask spread or explicitly by charging
> execution commissions

Illiquid assets can lead to economic crisis, as it happened with the
[Subprime mortgage
crisis](https://en.wikipedia.org/wiki/Subprime_mortgage_crisis). Given
my little knowledge in these topics, seems to me kind of surprising that
markets don't crash more frequently.

TODO What about the liquidity of tokens? 

## Bancor's solution to liquidity (V1)

[Bancor protocol white paper](https://storage.googleapis.com/website-bancor/2018/04/01ba8253-bancor_protocol_whitepaper_en.pdf)

We will only focus here on the mathematical reasoning of the proposed
protocol V1 as [explained](https://drive.google.com/file/d/0B3HPNP-GDn7aRkVaV3dkVl9NS2M/view) by Meni Rosenfeld.
There is a similar post on this topic by
[relevant.community from 2018](https://blog.relevant.community/how-to-make-bonding-curves-for-continuous-token-models-3784653f8b17).
And more generally you can find lots of information in the [Bancor network blog](https://blog.bancor.network/).

### Fractional-reserve banking

Before getting into bancor's protocol, we need to introduce
[Fractional-reserve banking](https://en.wikipedia.org/wiki/Fractional-reserve_banking). TODO

### Token price defined as the partial derivative of the reserve

Let's imagine we have a reserve in some value currency (e.g. dollars or
ETH) and we use to store value when someone buys tokens, and take value
from when someone sells them. Here we will use a single reserve holding
multiple tokens. See Meni Rosenfeld's
[document](https://drive.google.com/file/d/0B3HPNP-GDn7aRkVaV3dkVl9NS2M/view)
to see how it would apply for a single token hold in multiple reserves. 

Let's call $$r$$ the value hold in a reserve. We wish that the price of
a token tracks down the total supply of tokens: the more tokens there
are, the higher the price, the less there are the smaller the price. One
intuitive way to represent this, is to define price partial derivative of the
reserve with respect to the total supply of token $$s_i$$

$$p_i(s_i) = \frac{\partial r}{\partial s_i}$$

where by the index $$ _i$$ we mean some kind of token. We are imagining
that we can use the same reserve to trade multiple kinds of tokens.

$$r(s_1,...,s_n) = \sum_i f_i(p_i s_i)$$

The reason for using a function here is that later we can investigate it
later. Then, using the chain rule, the price of $$t_i$$ is

$$p_i(s_i) = f_i^{\prime}(p_i s_i)\left(\frac{\partial p_i }{\partial s_i}s_i + p_i\right)$$

where $$f_i^{\prime}$$ is the derivative of the function with respecto to its argument.

Finally, the value added or removed to the reserve ($$\Delta r$$)
upong a certain change in token supply $$x$$ is

$$\Delta r(x) = \int_{s_i}^{s_i+x} p_i(z) dz $$

So we have left is to pick a given $$f(...)$$. 

In the context of fractional-reserve banking, we pick a linear function
$$f_i(p_i s_i) = a_i p_i s_i$$ In particular $$0 < a_i \ge 1$$ to
maintain the meaning in "fractional". For example, taking $$a_i=0.5$$
means half the total value of the token supply $$p_i s_i$$ is in the
reserve.

Now, the price is the solution to the equation

$$p_i(s_i) = a_i\left(\frac{\partial p_i }{\partial s_i}s_i + p_i\right)$$

meaning that

$$p_i(s_i) = c s_i^{\frac{1}{a_i}-1} = p_i^0$$\left\frac{s_i}{s_i^0} \right^{\frac{1}{a_i}-1}$$

where $$s_i^0$$ and $$s_i^0$$ represents the initial price and token
supply respectively. In practice it can be any pair of values for which
the mapping is known. Before moving, it should mention that Wolfram
Alpha can
[solve](https://www.wolframalpha.com/input/?i=p+%3D+a*%28p%27x%2Bp%29)
the equation for you.

Note that we can solve this equation individually for any token bonding
curve $p_i$. So for any combination of token supplies

$$r(s_1,...) = \sum_i a_i p_i^0 \left\frac{s_i}{s_i^0} \right^{\frac{1}{a_i}-1} s_i$$

Then, if we exchange the supply from $$s_i$$ in $$x$$ by selling or
buying, what we pay or gain in the reserve currency is the
aforementioned integral

$$ \int_{s_i}^{s_i+x} p_i(z) dz = a_i p_i^0 \left \left 1 + \frac{x}{s_i}\right^{\frac{1}{a_i}}- 1 \right $$




### Interactive bancor bonding curve graphic
