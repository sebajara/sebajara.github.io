---
title: Bird identification guide using LaTex
date: 2020-07-24
tags: [LaTex, Tikz, web scraping, birding, Rock Creek Park]
header:
  image: "https://raw.githubusercontent.com/sebajara/birds/master/RockCreekPark/allaboutbirds/allaboutbirds_booklet-18.png"
excerpt: "Scraping bird identification info from Allaboutbirds and Audubon and turn them into an identification guide using LaTex"
mathjax: "true"
toc: true
toc_label: "Table of Contents"
toc_icon: "cog"
---

I enjoy taking walks doing bird-watching. Specially in DC there are many
near by parks, like the Rock Creek Park. I've always wanted a compact
and very visual guide to help me identify birds. Using pytho and LaTex,
I made a visual identification booklet, and a bird sighting
checklist. You can check the full code
at [sebajara/birds](https://github.com/sebajara/birds).

## Rock Creek Park Identification helper

One thing I constantly have troubles is having a quick reference to help
me identify birds. Some of the current phone apps are very good, but for
memorizing I find easier to have a booklet. So I decided make my own
identification guide.

To do this, I scraped the web pages associated to each bird in the check
list in the [Audubon](https://www.audubon.org) and
[Allaboutbirds](https://www.allaboutbirds.org/) sites, and downloaded
their pictures and some diagrams. 

Then, I organize them into a mini identification helper. Most work was
 actually selecting the most helpful pictures for each bird. Here is an
example page from the [identification
booklet](https://raw.githubusercontent.com/sebajara/birds/master/RockCreekPark/allaboutbirds/allaboutbirds_booklet.pdf):

![](https://raw.githubusercontent.com/sebajara/birds/master/RockCreekPark/allaboutbirds/allaboutbirds_booklet-15.png)

Note the resolution was reduced for making this example page. The bird
drawings are taken from [Audubon](https://www.audubon.org)'s site. The
bird pictures, as well as the "habitat", "food", "nesting", "behavior",
and "conservation" diagrams, are taken from the
[Allaboutbirds](https://www.allaboutbirds.org/)'s site.

I hope not to be violating any copy-write issues by sharing the
generated pdf. In case I do, please let me know and I will remove the
final product.

## Rock Creek Park bird checklist

The [Rock Creek Park](https://www.nps.gov/rocr/) gives a very useful
[bird
checklist](https://www.nps.gov/rocr/learn/nature/upload/birdchecklist.pdf). I
remade their table fit into one page checklist, and using color and
shape coding, which in my opinion makes it easier to use (see
[Birds_RockCreekPark.pdf](https://raw.githubusercontent.com/sebajara/birds/master/RockCreekPark/Birds_RockCreekPark.pdf))

![](https://raw.githubusercontent.com/sebajara/birds/master/RockCreekPark/Birds_RockCreekPark_example.png)

Instead of naming months by letters I am using numbers (1-12). Also, I
am using colors for coding sighting frequency categories 
<table>
  <thead>
    <tr>
      <th>Category</th>
      <th>Coding</th>
    </tr>
  </thead>
  <tfoot>
    <tr>
      <td>Unknown</td>
      <td>White</td>
    </tr>
  </tfoot>
  <tbody>
    <tr>
      <td>Common</td>
      <td>Green</td>
    </tr>
    <tr>
      <td>Uncommon</td>
      <td>Yellow</td>
    </tr>
    <tr>
      <td>Rare</td>
      <td>Red</td>
    </tr>
    <tr>
      <td>No sighting</td>
      <td>Black</td>
    </tr>
    <tr>
      <td>Nesting/Non-nesting</td>
      <td>Circled/Squared shape</td>
    </tr>
  </tbody>
</table>


<!--
### Example of coding in LaTex 

I am not a great coding in LaTex, but I though may be useful to show how
you can automate a lot while making figures with
[Tikz](https://en.wikibooks.org/wiki/LaTeX/PGF/TikZ).

What we want is some function that we pass the coordinates, the
bird-name, and a list with some coding of the colors and shape, and then
draw the corresponding row in the table. E.g.
{% highlight latex %}
{% raw %}
\begin{tikzpicture}[]
	\drawbirdbox{0}{0}{Catbird, Gray}{{5,5,3,3,2,2,2,2,1,3,3,5}};
\end{tikzpicture}
{% endraw %}
{% endhighlight %}
then we can divide it into individual operations. First translating
everything to some given x,y coordinates, drawing the box where the name
goes, writing the name, drawing and coloring the boxes on each month,
and finally adding the month numbers.

{% highlight latex %}
{% raw %}
\def\rowheight{0.35} % some height
\def\namewidth{4.1} % some width
% -- box for ticking observation
\newcommand{\drawtickingbox}[]{
  \draw[black!90] (0,0) rectangle ++(\rowheight,\rowheight);
}
% -- box where the name of the bird will appear
\newcommand{\drawnamebox}[]{
  \draw[black!90] (\rowheight,0) rectangle ++(\namewidth,\rowheight);
}
% -- write the name of the bird
\newcommand{\birdname}[1]{
  \node[anchor=base,label=right:{\small #1}] (0,0) at (0.5*\rowheight,0.45*\rowheight) {};
}
{% endraw %}
{% endhighlight %}

{% highlight latex %}
{% raw %}
% -- draw month boxes given a list of observation keys for all 12 months
\newcommand{\drawmonthboxes}[1]{% {observationKeyList}
  \foreach \obskey [count=\month] in #1 {
    \ifnum\month<10{ % single digit months
      \pgfmathparse{(\month)*\rowheight}
      \drawmonthbox{\namewidth+\pgfmathresult}{0}{\obskey}{0}
    }\fi
    \ifnum\month>9{ % double digit months
      \pgfmathparse{(\month+0.2*(\month-10))*\rowheight}
      \drawmonthbox{\namewidth+\pgfmathresult}{0}{\obskey}{1}
    }\fi
  }
}
{% endraw %}
{% endhighlight %}

{% highlight latex %}
{% raw %}
% -- draw the box for a single month (this time x,y are in absolute reference)
% Observation Key conventions:
% unknown             := 0
% common              := 1
% common-nesting      := 2
% uncommon            := 3
% uncommon-nesting    := 4
% rare                := 5
% rare-nesting        := 6
% none                := 7
\def\monthcolorslist{{"white","green!40","green!40","yellow!50","yellow!50","red!40","red!40","black!90"}}
\newcommand{\drawmonthbox}[4]{% {x}{y}{observationKey}{monthDigBoolean}
  \begin{scope}[shift={(#1,#2)}]
  \def\myindex{#3} % figure out the color
  \pgfmathparse{\monthcolorslist[\myindex]}
  \edef\mycolor{\pgfmathresult}
  \ifnum#4=0{ % single digit month
    \draw[black!90,fill={\mycolor}] (0,0) rectangle ++(\rowheight,\rowheight);
    \ifnum#3=2{ \drawnestingsign }\fi
    \ifnum#3=4{ \drawnestingsign }\fi
    \ifnum#3=6{ \drawnestingsign }\fi
  }\fi
  \ifnum#4=1{ % double digit month
    \draw[black!90,fill={\mycolor}] (0,0) rectangle ++(1.2*\rowheight,\rowheight);
    \ifnum#3=2{ \drawnestingsigndig }\fi
    \ifnum#3=4{ \drawnestingsigndig }\fi
    \ifnum#3=6{ \drawnestingsigndig }\fi
  }\fi
  \end{scope}
}
{% endraw %}
{% endhighlight %}

{% highlight latex %}
{% raw %}
\def\nestingcolor{black!90}
% -- draw the nesting sign for a single digit month
\newcommand{\drawnestingsign}[]{
	\draw[fill=\nestingcolor] (0,0) -- (0.5*\rowheight,0) to[out=180,in=-90] (0,0.5*\rowheight)  -- cycle;
    \draw[fill=\nestingcolor] (0.5*\rowheight,0) -- (\rowheight,0) -- (\rowheight,0.5*\rowheight) to[out=-90,in=0] cycle;
    \draw[fill=\nestingcolor] (0,\rowheight) -- (0.5*\rowheight,\rowheight) to[out=180,in=90] (0,0.5*\rowheight)  -- cycle;
    \draw[fill=\nestingcolor] (0.5*\rowheight,\rowheight) -- (\rowheight,\rowheight) -- (\rowheight,0.5*\rowheight) to[out=90,in=0] cycle;
}
% -- draw the nesting sign for a double digit month
\newcommand{\drawnestingsigndig}[]{
    \draw[fill=\nestingcolor] (0,0) -- (0.5*1.2*\rowheight,0) to[out=180,in=-90] (0,0.5*\rowheight)  -- cycle;
    \draw[fill=\nestingcolor] (0.5*1.2*\rowheight,0) -- (1.2*\rowheight,0) -- (1.2*\rowheight,0.5*\rowheight)  to[out=-90,in=0] cycle;
    \draw[fill=\nestingcolor] (0,\rowheight) -- (0.5*1.2*\rowheight,\rowheight) to[out=180,in=90] (0,0.5*\rowheight)  -- cycle;
    \draw[fill=\nestingcolor] (0.5*1.2*\rowheight,\rowheight) -- (1.2*\rowheight,\rowheight) -- (1.2*\rowheight,0.5*\rowheight) to[out=90,in=0] cycle;
}
{% endraw %}
{% endhighlight %}
-->
