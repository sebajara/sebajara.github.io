---
title: Bancor protocol bonding curve (V1)
date: 2020-07-26
tags: [Economics, Cryptocurrency, Token Bonding Curve, Fractional-reserve, Bancor, Mathematical modeling, Interactive]
excerpt: "Motivated by developments in ways to create local community currencies, I try to explain the reasoning behind bancor's protocol (version 1)."
mathjax: "true"
toc: true
toc_label: "Jump to:"
toc_icon: "fast-forward"
---

NOTE: this a post in the making.

TODO. General intro. Motivation. CIC.

## Crypto-tokens and their price

What is a [crypto-token](https://www.investopedia.com/terms/c/crypto-token.asp)?
In simple terms are a kind of cryptocurrency that represents one unit of
something that can be used. We will try to deal with the problem of how
such token should be priced, which given the experience with [bitcoin
volatility](https://www.investopedia.com/articles/investing/052014/why-bitcoins-value-so-volatile.asp),
seems like an important issue. Specially if we mean to use tokens as way
for people to create community currencies.

### The liquidity problem

An immediate problem with setting the price of a token is
"liquidity". Wikipedia defines [market
liquidity](https://en.wikipedia.org/wiki/Market_liquidity) as

> a market's feature whereby an individual or firm can quickly purchase
> or sell an asset without causing a drastic change in the asset's
> price.

Liquidity is very important for a healthy economy, as illiquid assets
can lead to economic crisis (e.g. the [Subprime mortgage
crisis](https://en.wikipedia.org/wiki/Subprime_mortgage_crisis).

If you are under the intuition that money is a physical thing, it may be
difficult to grasp immediately why liquidity can become a problem. But
economies can run on anything that people are *willing* to trade with;
and over time, markets have become more rich in their means to do
so (e.g. see the wiki entry of [assets](https://en.wikipedia.org/wiki/Asset)). 

Intuitively, prices are set based on how much people are *willing* to
trade. So in practical terms, liquidity amounts to the following: for
any amount of asset I buy for a given price, there is someone else
*willing* to buy it from me. How liquidity *ensured* in regular markets?
Liquidity is facilitated by [Market
Makers](https://en.wikipedia.org/wiki/Market_maker), which buy and sell
assets making some profit from a bet on future price or by charging a
commission.

So deciding how tokens are priced is crucial, if they intend to be used
as stable means for trade.

## Token bonding curves

Here comes the bonding curve. In simple terms, a token bonding curve is
a function $$p(s)$$ that gives the value of one unit of token in some
given currency units, where $$s$$ is total supply of tokens in
circulation. Then to buy or sell a given amount of token, we integrate
$$p(s)$$ to calculate the price. If you want to learn more about
bonding-curves checkout the blog posts by
[yos.io](https://yos.io/2018/11/10/bonding-curves/), 
[relevant.community](https://blog.relevant.community/how-to-make-bonding-curves-for-continuous-token-models-3784653f8b17),
, and [coinmonks](https://medium.com/coinmonks/token-bonding-curves-explained-7a9332198e0e).

Bonding curves were first proposed in the context of "[curation
markets](https://medium.com/@simondlr/introducing-curation-markets-trade-popularity-of-memes-information-with-code-70bf6fed9881)",
where tokens were already operating under certain rules. In particular:
* A token that can be minted at any time (continuous) according to a
  price set by the smart contract.
* This price gets more expensive as more tokens are in circulation.
* The amount paid for the token is kept in a communal reserve.
* At any point in time, a token can be withdrawn (“burned”) from the
  active supply, and a proportional part of the communal reserve can be
  taken with.
Let's unpack a few terms. 

Smart contracts are code that can be attached to tokens to perform
certain functions automatically. The bonding curve would be the function
that smart contracts implement to calculate prices. See particularly
the post by [yos.io](https://yos.io/2018/11/10/bonding-curves/) on how
bonding curve smart contracts can be implemented.

The second important term is the one of "reserve". I was not aware, but
the idea is quite old (see [Fractional-reserve
banking](https://en.wikipedia.org/wiki/Fractional-reserve_banking) on
Wikipedia). In the context of a bonding curve, the reserve would be some
some way to store and update the total value of token supply, such that
for every buy/sell of tokens, the value is added/subtracted to/from the
reserve.

## Bancor's protocol V1 

Now the question is: what bonding curve function we pick in order to
satisfy its conditions? Here comes the Bancor protocol (see its [white
paper](https://storage.googleapis.com/website-bancor/2018/04/01ba8253-bancor_protocol_whitepaper_en.pdf)).
I will only discuss here the mathematical reasoning of the protocol V1
as in this
[pdf](https://drive.google.com/file/d/0B3HPNP-GDn7aRkVaV3dkVl9NS2M/view)
from Meni Rosenfeld. If you are interested, you can find more
information in the [Bancor network blog](https://blog.bancor.network/).  <!-- If you are
interested, the post by [relevant.community from
2018](https://blog.relevant.community/how-to-make-bonding-curves-for-continuous-token-models-3784653f8b17)
discuss similar -->

Here for illustration purposes, we will use a single reserve holding a
single token. Let's imagine we have a reserve in some currency
(e.g. dollars or ETH) and we use it to store value when someone buys
tokens, and take value from when someone sells them. We explained
previously that we demand certain properties:
* *Monotonic Bonding curve:* The bonding curve should be a monotonic
function of the total tokens in circulation (supply). The higher the
supply, the higher the price, and vice-versa. 
* *Cost/Gain as integral of bonding curve*: the gain or cost from
selling or buying tokens should be the integral of the bonding
curve, and that amount is updated to the reserve. Note tha because the
curve is monotonic, the amounts are reversible.
* *Fractional reserve*: The relation between the value stored in the
reserve and the supply should be invariant to changes in
supply. Basically that if we define the reserve to hold 20% of the
supply, it should always hold 20%.
* Also, we want that the price for a supply of 0 should be also 0.

Note that particularly the first and second solve the liquidity
problem. The rest are more or less particulars of the implementation.

### Token price as the derivative of the reserve.

Let's call $$r$$ the value hold in a reserve. One intuitive way to
represent the first condition we demanded is to define price as the
derivative of the reserve with respect to the total supply of tokens
$$s$$

$$p(s) = \frac{d r}{d s}$$

For generality, let's encode the third property as saying that the value
of the reserve is some function of the total value of the supply

$$r(s) = f(p s)$$

Now note that we can use the chain rule, and we find that the price
should satisfy

$$p(s) = f^{\prime}(p s)\left(\frac{d p }{d s}s + p\right)$$

where $$f^{\prime}(...)$$ is the derivative of the function with respec
to its argument.

How we pick $$f(...)$$? In the context of fractional-reserve banking,
$$f(...)$$ is a linear function $$f(p s) = a p s$$, and in order to
maintain the meaning of "fractional", the constant $$a$$ should be in
the rage $$0 < a \le 1$$. For example, picking $$a=0.5$$ means that half
the total value of the token supply $$p s$$ is in the reserve at all
times.

Based on our previous definitions, the price must satisfy

$$ p(s) = a\left(\frac{d p }{d s}s + p\right)$$

so the bonding curve is (see
[link](https://www.wolframalpha.com/input/?i=p+%3D+a*%28p%27x%2Bp%29)
for solving the equation with Wolfram Alpha)

$$ p(s) = p_0 \left( \frac{s}{s_0} \right)^{\frac{1}{a}-1}$$

where $$p_0$$ and $$s_0$$ represent some pair of price and token supply
values for which the mapping is known. In practice, these are typically
the initial values.

Then we can obtain the value of the reserve by replacing $$p$$ on $$aps$$

$$r(s) = f(ps) = aps = a p_0 s_0^{1-\frac{1}{a}} s^{\frac{1}{a}} $$

### Buying or selling tokens

Say we wish to change the supply from $$s_0$$ to $$s_0+\Delta s$$ by
buying or selling tokens. How much we pay/get in the units of the
reserve currency? Let's call this value $$\Delta r$$. Then using the
function $$r(s)$$

$$\begin{array}{rcl}
	\Delta r & = & r(s_0 + \Delta s) - r(s_0) \\
	\Delta r & = & a p_0 s_0^{1-\frac{1}{a}} \left( \left(s_0 + \Delta s \right)^{\frac{1}{a}} - s_0^{\frac{1}{a}} \right)\\
	\Delta r & = & a p_0 s_0 \left( \left(1 + \frac{\Delta s}{s_0} \right)^{\frac{1}{a}} - 1 \right)
\end{array}
$$

In case we want to sell or buy tokens for a given amount of currency, we
can invert the previous relation to obtain

$$\begin{array}{rcl}
	\Delta r & = & a p_0 s_0 \left( \left(1 + \frac{\Delta s}{s_0} \right)^{\frac{1}{a}} - 1 \right) \\
	\frac{\Delta r}{a p_0 s_0} & = &  \left(1 + \frac{\Delta s}{s_0} \right)^{\frac{1}{a}} - 1 \\
	\left( \frac{\Delta r}{a p_0 s_0} + 1 \right)^a & = & \frac{\Delta s}{s_0} + 1
	s_0 \left(\left( \frac{\Delta r}{a p_0 s_0} + 1 \right)^a - 1 \right) & = & \Delta s
\end{array}
$$

So using these two equations we can map reserve currency to amount of
tokens for any given purchase or sell transaction.

### Interactive bancor bonding curve graphic

<!--
## Potential explorations

$$ \Delta s =  s \left( \left( 1 + \frac{\Delta r}{a p_0 s_0}\right)^{a}- 1 \right) $$

Here are a few ideas:
* Generalize to multiple reserves in multiple tokens. As a network, is
  there a benefit on having certain network topology?
* Explore using negative values for constants $$a_i$$ as a way to encode
  "dislikes economies" (e.g. something like carbon credit).
* Can we formalize what we expect from the price and reserve/token
  functions in different cases? E.g. volatility, caps, etc. Then see how
  changing their form relates to those criterias?
 --> 

