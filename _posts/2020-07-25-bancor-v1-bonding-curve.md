---
title: Bancor protocol bonding curve (V1)
date: 2020-07-27
tags: [Economics, Cryptocurrency, Token Bonding Curve, Fractional-reserve, Bancor, Mathematical modeling, Interactive]
header:
  image: "/assets/images/bancor_bonding_curve_interactive_example.png"
excerpt: "Motivated by developments in ways to create local community currencies, I try to explain the reasoning behind bancor's protocol (version 1)."
mathjax: "true"
toc: true
toc_label: "Jump to:"
toc_icon: "fast-forward"
---

TODO. General intro. Motivation. CIC.

## Crypto-tokens and their price

What is a [crypto-token](https://www.investopedia.com/terms/c/crypto-token.asp)?
In simple terms, they are a class of cryptocurrencies that represent
something that can be used withing the blockchain. 

We will be interested problem of how such token should be priced, which
given the experience with [bitcoin
volatility](https://www.investopedia.com/articles/investing/052014/why-bitcoins-value-so-volatile.asp),
seems like an important issue. Specially relevant if we mean to use
tokens as way for people to create community currencies.

### The liquidity problem

An immediate problem with setting the price of a token is
"liquidity". Wikipedia defines [market
liquidity](https://en.wikipedia.org/wiki/Market_liquidity) as

> a market's feature whereby an individual or firm can quickly purchase
> or sell an asset without causing a drastic change in the asset's
> price.

If you are under the intuition that money is a physical thing, it may be
difficult to grasp immediately why liquidity can become a problem. But
economies can run on anything that people are *willing* to trade with;
and over time, markets have become richer in their means to do
so (e.g. see the wiki entry of [assets](https://en.wikipedia.org/wiki/Asset)). 

Intuitively, prices are set based on how much people are *willing* to
trade. So in practical terms, liquidity amounts to the following: for
any amount of asset I buy for a given price, I can also sell it for
approximately the same price. Somewhat similar to the conservation of
energy in a reversible path if we were talking about physical
systems. How is liquidity *ensured* in regular markets?  Liquidity is
facilitated by [Market
Makers](https://en.wikipedia.org/wiki/Market_maker), which buy and sell
assets making some profit from a bet on future price or by charging a
commission. Liquidity is very important for a healthy economy, as
illiquid assets can lead to economic crisis (e.g. the [Subprime mortgage
crisis](https://en.wikipedia.org/wiki/Subprime_mortgage_crisis).

So deciding how tokens are priced is crucial, if they intend to be used
as stable means for trade.

## Token bonding curves

In simple terms, a token bonding curve is a function $$p(s)$$ that takes
the total supply of tokens in circulation $$s$$, and returns the price
per token in some given currency units. Then to buy or sell a given
amount of token, we integrate $$p(s)$$ to calculate the price. The
simplest case is a constant price, where the integral is proportional to
the amount of token. If you want to learn more about bonding-curves
check out the blog posts by
[yos.io](https://yos.io/2018/11/10/bonding-curves/), 
[relevant.community](https://blog.relevant.community/how-to-make-bonding-curves-for-continuous-token-models-3784653f8b17),
, and [coinmonks](https://medium.com/coinmonks/token-bonding-curves-explained-7a9332198e0e).

Bonding curves were first proposed by XX in what he coined "[curation
markets](https://medium.com/@simondlr/introducing-curation-markets-trade-popularity-of-memes-information-with-code-70bf6fed9881)",
where tokens should operate under certain rules:
* A token can be minted at any time (continuous) according to a price
  set by the smart contract.
* This price gets more expensive as more tokens are in circulation.
* The amount paid for the token is kept in a communal reserve.
* At any point in time, a token can be withdrawn (“burned”) from the
  active supply and a proportional part of the communal reserve can be
  taken with.
Let's unpack a few terms. 

In our context, a [smart
contract](https://en.wikipedia.org/wiki/Smart_contract) is code that can
be attached to tokens such that they perform certain functions
automatically. In our case, the bonding curve is the function that smart
contracts implement to calculate the prices of tokens. The post by
[yos.io](https://yos.io/2018/11/10/bonding-curves/) is very good at
explaining the implementation side of the bonding curve.

The second important term is the one of "reserve". In the context of a
bonding curve, the reserve would be some way to store and update
the total value of token supply, such that for every buy/sell
transaction of tokens, the value is added/subtracted to/from the
reserve. I was not aware, but the idea is quite old and commonly used,
e.g. see [Fractional-reserve
banking](https://en.wikipedia.org/wiki/Fractional-reserve_banking) on
Wikipedia.

## Axiomatic approach to Bancor's protocol 

So what function for the bonding curve should we pick? Bancor in their
protocol version 1 (V1) propose a particular set of equations.  I will
try to explain the argument, as defined by Meni Rosenfeld in this
[pdf](https://drive.google.com/file/d/0B3HPNP-GDn7aRkVaV3dkVl9NS2M/view). I've
been thinking of using an "axiomatic" approach to explain the
protocol. The idea will be to define what we want out of the system as a
set of principles and then infer the equations that satisfy those
principles. For illustration purposes, I will use a single reserve
holding a single token. If you are interested to learn more about bancor
(e.g. the version 2 of the protocol), you can find more information in
the [Bancor network blog](https://blog.bancor.network/).

Now, here is my attempt at formally defining the principles of the
bonding curve. We wish that the reserve, the supply, and the bonding
curve satisfy these properties:
* *Strictly Monotonic Bonding curve:* The bonding curve should be a
[strictly monotonic](https://en.wikipedia.org/wiki/Monotonic_function)
function of the total tokens in circulation (supply). The higher the
supply, the higher the price, and vice-versa.
* *Cost/Gain as integral of bonding curve*: the gain or cost from
selling or buying tokens should be the integral of the bonding curve,
and that amount is updated to the reserve. Note that because the curve
is strictly monotonic, the amounts are reversible.
* *Fractional reserve*: The relation between the value stored in the
reserve and the supply should be invariant to changes in
supply. Basically that if we define the reserve to hold 20% of the
supply, it should always hold 20%.
* *Bonding curve starts from the origin*: the price for a supply of 0
  should be also 0.

Note that the first and second conditions can solve the liquidity
problem. The third condition is particular to the fractional-reserve
implementation, and the last one captures the intuition that the curve
should start from 0. Now, let's see how to derive the bonding curve.

### Derivation of the bonding curve

Let's imagine we have a reserve in some currency (e.g. dollars or ETH)
and we use it to store value when someone buys tokens, and take the
value from when someone sells them.

Let's call $$r$$ the value hold in a reserve. One intuitive way to
represent the first condition we demanded is to define price as the
derivative of the reserve with respect to the total supply of tokens
$$s$$

$$p(s) = \frac{d r}{d s}$$

To encode fractional-banking, the value of the reserve should be a
linear function of the total value in the supply, which is
$$p(s)$$ times $$s$$

$$r(s) = a p(s) s $$

and to maintain the "fractional" meaning, the constant $$a$$ should be
in the range $$0 < a \le 1$$. For example, picking $$a=0.5$$ means that
half the total value of the token supply $$p s$$ is in the reserve at
all times.

Let's see how to obtain $$p(s)$$ and $$r(s)$$. First, note that by using
the chain rule the price should satisfy the following equation

$$p(s) = r^{\prime}(s)\left(\frac{d p }{d s}s + p\right) = a\left(\frac{d p }{d s}s + p\right)$$

which is enough to derive the bonding curve $$p(s)$$ (see this
[link](https://www.wolframalpha.com/input/?i=p+%3D+a*%28p%27x%2Bp%29)
for the solution using Wolfram Alpha web app)

$$ p(s) = p_0 \left( \frac{s}{s_0} \right)^{\frac{1}{a}-1}$$

where $$p_0$$ and $$s_0$$ represent some pair of price and token supply
values for which the mapping is known, e.g. their initial values.

Finally, we can obtain the value of the reserve by replacing $$p(s)$$ 

$$r(s) = ap(s)s = a p_0 s_0^{1-\frac{1}{a}} s^{\frac{1}{a}} $$

### Buying and selling tokens

Say we wish to change the supply from $$s_0$$ to $$s_0+\Delta s$$ by
buying or selling tokens. How much we should pay or may get in the units
of the reserve currency? Let's call this value $$\Delta r$$. Then using
the function $$r(s)$$

$$\begin{array}{rcl}
	\Delta r & = & r(s_0 + \Delta s) - r(s_0) \\
	\Delta r & = & a p_0 s_0^{1-\frac{1}{a}} \left( \left(s_0 + \Delta s \right)^{\frac{1}{a}} - s_0^{\frac{1}{a}} \right)\\
	\Delta r & = & a p_0 s_0 \left( \left(1 + \frac{\Delta s}{s_0} \right)^{\frac{1}{a}} - 1 \right)
\end{array}
$$

In case we want to sell or buy tokens for a given amount of currency, we
can invert the previous relation to obtain

$$\begin{array}{rcl}
	a p_0 s_0 \left( \left(1 + \frac{\Delta s}{s_0} \right)^{\frac{1}{a}} - 1 \right) & = & \Delta r \\
	\left(1 + \frac{\Delta s}{s_0} \right)^{\frac{1}{a}} - 1 & = & \frac{\Delta r}{a p_0 s_0}  \\
	\frac{\Delta s}{s_0} + 1 & = & \left(1 +  \frac{\Delta r}{a p_0 s_0} \right)^a \\
	\Delta s & = & s_0 \left(\left( 1 + \frac{\Delta r}{a p_0 s_0} \right)^a - 1 \right)
\end{array}
$$

Then, using these two equations we can map reserve currency to the
amount of tokens for any given purchase or sell transaction.

### Interactive graphic

I made an interactive graphic using bokeh (see the script used to
generate the graphic
[here](https://raw.githubusercontent.com/sebajara/sebajara.github.io/master/python/2020_07_26_bancor_v1_bonding_curve.py))
to get an intuition for what the parameters mean. Note that changing the
reserve fraction $$a$$ has a very strong effect on the curves. In
particular, the smaller $$a$$ the less incentive there is for selling
tokens and this property is what CIC uses to promote the local currency
to remain within the community.

{% include blog-aux/2020_07_26_bancor_v1_bonding_curve.html %}

## Concluding remarks

I find the very exciting the idea that conversion rates between
currencies can be hardcoded formally, and that we can exploit some of
their properties to assist communities less favored by the economic
system's *status quo*, as the CIC is doing in Africa. I hope to have
shown here how we can start from certain properties or axioms that we
wish the system to have, and then derive the corresponding formulas, and
understand a bit better what they mean. The result here depends heavily
on the idea of a fractional-reserve, which for CIC acts as a way to
preserve the value of the collateral relative to the total token supply,
and allows using the parameter $$a$$ as a way to increase the value of
the collateral initially (by a factor of $$1/a$$), and discourage cashing
out the local community currency.

In the future, would be interesting to explore different axioms for
setting bonding curves. For example, I've been thinking that we could
create a token representing carbon emissions, or something else we wish
to avoid. Then use the token for trading such that we incentivize
diminishing those bad outcomes. First of all, we would need some kind of
negative supply-reserve relation. But more generally, it is unclear what
mapping the supply to the reserve would be best suited, *a priori* why
should be fractional? By having a clear derivation procedure, perhaps we
could ask how our market design (axioms) generate different curves and
find one that *best* guarantees avoiding worst-case scenarios. Another
area of exploration would encode different properties of tokens into the
framework, such as volatility into the bonding curves. I hope to explore
some of these questions in future posts.

<!--

## Potential advantages of the formulasusi

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

