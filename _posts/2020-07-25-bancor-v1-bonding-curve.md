---
title: Bancor V1 bonding curve
date: 2020-07-25
tags: [Economics, Bancor, Token Bonding Curve, Fractional Reserve]
excerpt: "Explanation of the reasoning behind bancor's protocol V1 + an interactive bonding curve application"
mathjax: "true"
toc: true
toc_label: "Jump to:"
toc_icon: "fast-forward"
---

NOTE: this a post in the making.

TODO. General overview.

## Personal motivations 

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
my little knowledge in these topics, the more I learn, the more
surprising the stability of economic systems appears to me.

What about the liquidity of tokens? TODO

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
a single token. See Meni Rosenfeld's
[document](https://drive.google.com/file/d/0B3HPNP-GDn7aRkVaV3dkVl9NS2M/view)
to see how it would apply for a single token hold in multiple reserves. 

Let's call $$r$$ the value hold in a reserve. We wish that the price of
a token tracks down the total supply of tokens: the more tokens there
are, the higher the price, the less there are the smaller the price. One
intuitive way to represent this, is to define price partial derivative of the
reserve with respect to the total supply of token $$s$$

$$p(s) = \frac{d r}{d s}$$

For generality, let's say the value of the reserve is some function of
the total value of the supply

$$r(s) = f(p s)$$

Using the chain rule the price is

$$p(s) = f^{\prime}(p s)\left(\frac{d p }{d s}s + p\right)$$

where $$f^{\prime}(...)$$ is the derivative of the function with respecto to
its argument. 

So we have left is to pick a given $$f(...)$$. In the context of
fractional-reserve banking, we pick a linear function $$f(p s) = a p s$$
In particular the range $$0 < a \le 1$$ to maintain the meaning in
"fractional". For example, taking $$a=0.5$$ means half the total value
of the token supply $$p s$$ is in the reserve.

Now, the price is the solution to the equation 

$$p(s) = a\left(\frac{d p }{d s}s + p\right)$$

meaning that ([see link for solving the equation](https://www.wolframalpha.com/input/?i=p+%3D+a*%28p%27x%2Bp%29))

$$p(s) = p_0 \left( \frac{s}{s_0} \right)^{\frac{1}{a}-1} $$

where $$p_0$$ and $$s_0$$ represents the initial price and token supply
respectively. In practice, could have picked any pair of values for
which the mapping is known.

Then we can obtain the value of the reserve by replacing $$p$$ on $$aps$$

$$r(s) = f(ps) = aps = a p_0 s_0^{1-\frac{1}{a}} s^{\frac{1}{a}} $$

### Buying or selling tokens

Say we wish to change the supply from $$s$$ to $$s+\Delta s$$ by buying
or selling tokens. How much we pay/get in the reserve currency?

Let's call the value added or removed to the reserve $$\Delta r$$. Then

$$ \Delta r = \int_{s}^{s+\Delta s} p(z)dz = a p_0 s_0 \left( \left( 1 + \frac{\Delta s}{s}\right)^{\frac{1}{a}}- 1 \right) $$

The integration is rather long, see Meni Rosenfeld's
[document](https://drive.google.com/file/d/0B3HPNP-GDn7aRkVaV3dkVl9NS2M/view). 

In case we want to sell or buy tokens for a given amount of currency, we
can invert the previous relation to obtain

$$ \Delta s =  s \left( \left( 1 + \frac{\Delta r}{a p_0 s_0}\right)^{a}- 1 \right) $$

Using these two equations we can map reserve currency to amount of
tokens for any given purchase or sell transaction.

### Interactive bancor bonding curve graphic

<!--
## Potential explorations

Here are a few ideas:
* Generalize to multiple reserves in multiple tokens. As a network, is
  there a benefit on having certain network topology?
* Explore using negative values for constants $$a_i$$ as a way to encode
  "dislikes economies" (e.g. something like carbon credit).
* Can we formalize what we expect from the price and reserve/token
  functions in different cases? E.g. volatility, caps, etc. Then see how
  changing their form relates to those criterias?
 --> 
