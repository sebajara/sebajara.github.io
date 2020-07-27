from bokeh.models import ColumnDataSource, CustomJS, Slider, HoverTool
from bokeh.plotting import Figure
from bokeh.layouts import row, column
from bokeh.io import output_file, show

# output html file
output_file('../_includes/blog-aux/2020_07_26_bancor_v1_bonding_curve.html', mode='cdn')

# parameters of the function
a = 0.25
s0 = 100
p0 = 1

# make our lists
x1 = [2*(n/100)*a*s0*p0 for n in range(0, 100)]
y1 = [p0 * ((s/s0) ** (1/a-1)) for s in x1]
x2 = [s0*(n/50) for n in range(-50, 50)]
y2 = [a*p0*s0*((1 + ds/s0)**(1/a) - 1) for ds in x2]

# ColumnDataSource
source = ColumnDataSource(data=dict(x1=x1, y1=y1, x2=x2, y2=y2))

# make our figure with the labels and plot the data
green = (0, 100, 0)
blue = (0, 0, 150)
pw = 300
ph = 300

# Bancor's Bonding Curve
plots = [0, 0, 0]
plots[0] = Figure(plot_width=pw, plot_height=ph,
                  title="Bonding Curve",
                  x_axis_label="Total tokens in circulation (s)",
                  y_axis_label="Price per token (p)")

plots[0].line(x='x1', y='y1', source=source, line_width=5, line_alpha=0.6, color=green)
plots[0].add_tools(HoverTool(tooltips=[('Supply', '@x1 tokens'), ('Price', '$@y1')],
                             mode='vline'))

# Buying/selling at Fixed token change
plots[1] = Figure(plot_width=pw, plot_height=ph,
                  title="Buying/Selling Curve",
                  x_axis_label="Token supply change (Δs)",
                  y_axis_label="Reserve change (Δr)")
plots[1].line(x='x2', y='y2', source=source, line_width=5, line_alpha=0.6, color=blue)
plots[1].add_tools(HoverTool(tooltips=[('Buy / Sell', '@x2 tokens'), ('Cost / Gain', '$@y2')],
                             mode='vline'))

# Buying/selling at Fixed reserve change
plots[2] = Figure(plot_width=pw, plot_height=ph,
                  title="Buying/Selling Curve",
                  x_axis_label="Reserve change (Δr)",
                  y_axis_label="Token supply change (Δs)")
plots[2].line(x='y2', y='x2', source=source, line_width=5, line_alpha=0.6, color=blue)
plots[2].add_tools(HoverTool(tooltips=[('Cash out / Pay', '$@y2'), ('Lose / Gain', '$@x2 tokens')],
                             mode='vline'))

# set font size for all plots
for n in range(0, 3):
    plots[n].title.text_font_size = '16pt'
    plots[n].xaxis.axis_label_text_font_size = "12pt"
    plots[n].yaxis.axis_label_text_font_size = "12pt"

# make 3 sliders, one for each parameter.
slider1 = Slider(start=0.01, end=1, value=a, step=.01, title="fraction (a)")
slider2 = Slider(start=0.01, end=200, value=s0, step=1, title="Initial supply (s0)")
slider3 = Slider(start=0.01, end=10, value=p0, step=0.1, title="Initial price (p0)")

# make a callback in JS for each slider to call, so can add the graphic
# as a standalone. The only important bit is to add the other objects in
# the arguments, such that bokeh knows how to replace stuff when
# generating the JS.
callback = CustomJS(args=dict(source=source, slider1=slider1, slider2=slider2, slider3=slider3), code="""
    var data = source.data;
    var f = slider1.value
    var s = slider2.value
    var p = slider3.value
    var x1 = data['x1']
    var y1 = data['y1']
    var x2 = data['x2']
    var y2 = data['y2']
    for (var i = 0; i < x1.length; i++) {
        x1[i] = 2*(i/x1.length)*f*s*p
        y1[i] = p*Math.pow(x1[i]/s, 1/f-1)
        x2[i] = s*((i/x2.length - 0.5))
        y2[i] = f*p*s*(Math.pow(1+x2[i]/s, 1/f)-1)
    }
    source.change.emit();
""")

# add the callback to the sliders
slider1.js_on_change('value', callback)
slider2.js_on_change('value', callback)
slider3.js_on_change('value', callback)

# organize into rows and columns, then show it
show(row(column(plots[0], slider1, slider2, slider3),
         column(plots[1], plots[2])))

#show(row(column(slider1, slider2, slider3),
#         plots[0], plots[1], plots[2]))
