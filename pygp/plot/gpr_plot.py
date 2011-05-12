"""
pygp plotting tools
===============================

Tools to plot Gaussian process :py:class:`pygp.gp` regression output.

"""

# import python / numpy:
import pylab as PL
import scipy as S
import matplotlib

def plot_training_data(x,y,
                       shift=None,
                       replicate_indices=None,
                       format_data={'alpha':.5,
                                    'marker':'.',
                                    'linestyle':'--',
                                    'lw':1,
                                    'markersize':9}):
    """
    Plot training data input x and output y into the
    active figure (See http://matplotlib.sourceforge.net/ for details of figure).

    Instance plot without replicate groups:
    
    .. image:: ../images/plotTraining.png
       :height: 8cm
       
    Instance plot with two replicate groups and a shift in x-koords:
    
    .. image:: ../images/plotTrainingShiftX.png
       :height: 8cm

    **Parameters:**

    x : [double]
        Input x (e.g. time).

    y : [double]
        Output y (e.g. expression).

    shift : [double]
        The shift of each replicate group.
        
    replicate_indices : [int]
        Indices of replicates for each x, rexpectively

    format_data : {format}
        Format of the data points. See http://matplotlib.sourceforge.net/ for details. 
        
    """
    x = S.array(x).reshape(-1)
    y = S.array(y).reshape(-1)

    x_shift = x.copy()

    if shift is not None and replicate_indices is not None:
        assert len(shift)==len(S.unique(replicate_indices)), 'Need one shift per replicate to plot properly'

        _format_data = format_data.copy()
        _format_data['alpha'] = .2
        
        number_of_groups = len(S.unique(replicate_indices))
        
        for i in S.unique(replicate_indices):
            x_shift[replicate_indices==i] -= shift[i]

        for i in S.unique(replicate_indices):
            col = matplotlib.cm.jet(256.* (i / (1. * number_of_groups)))
            _format_data['color'] = col
            PL.plot(x[replicate_indices==i],y[replicate_indices==i],**_format_data)
#            for i in S.arange(len(replicate_indices))[replicate_indices==i]:
#                PL.annotate("",xy=(x_shift[i],y[i]),
#                            xytext=(x[i],y[i]),
#                            arrowprops=dict(facecolor
#                                            =col,
#                                            alpha=.3,
#                                            shrink=.2,
#                                            frac=.3))
            #PL.plot(x,y,**_format_data)

        

    if(replicate_indices is not None):
        number_of_groups = len(S.unique(replicate_indices))
        format_data['markersize']=13
        format_data['alpha']=1
        for i in S.unique(replicate_indices):
            col = matplotlib.cm.jet(256.* (i / (1. * number_of_groups)))
            format_data['color'] = col
            PL.plot(x_shift[replicate_indices==i],y[replicate_indices==i],**format_data)
    else: PL.plot(x_shift,y,**format_data)
        
#    return PL.plot(x_shift,y,**format_data)

def plot_sausage(X,mean,std,alpha=None,format_fill={'alpha':0.3,'facecolor':'k'},format_line=dict(alpha=1,color='g',lw=3, ls='dashed')):
    """
    plot saussage plot of GP. I.e:

    .. image:: ../images/sausage.png
      :height: 8cm

    **returns:** : [fill_plot, line_plot]
        The fill and the line of the sausage plot. (i.e. green line and gray fill of the example above)
        
    **Parameters:**

    X : [double]
        Interval X for which the saussage shall be plottet.
        
    mean : [double]
        The mean of to be plottet.
        
    std : [double]
        Pointwise standard deviation.

    format_fill : {format}
        The format of the fill. See http://matplotlib.sourceforge.net/ for details.

    format_line : {format}
        The format of the mean line. See http://matplotlib.sourceforge.net/ for details.
        
    """
    X = X.squeeze()
    Y1 = (mean+2*std)
    Y2 = (mean-2*std)
    if(alpha is not None):
        old_alpha_fill = min(1, format_fill['alpha']*2)
        for i,a in enumerate(alpha[:-2]):
            format_fill['alpha'] = a * old_alpha_fill
            hf=PL.fill_between(X[i:i+2],Y1[i:i+2],Y2[i:i+2],lw=0,**format_fill)
        i+=1
        hf=PL.fill_between(X[i:],Y1[i:],Y2[i:],lw=0,**format_fill)
    else:
        hf=PL.fill_between(X,Y1,Y2,**format_fill)
    hp=PL.plot(X,mean,**format_line)
    return [hf,hp]



class CrossRect(matplotlib.patches.Rectangle):
    def __init__(self, *args, **kwargs):
        matplotlib.patches.Rectangle.__init__(self, *args, **kwargs)
        
        #self.ax = ax

    # def get_verts(self):
    #     rectverts = matplotlib.patches.Rectangle.get_verts(self)
        
    #     return verts

    def get_path(self, *args, **kwargs):
        old_path = matplotlib.patches.Rectangle.get_path(self)
        verts = []
        codes = []
        for vert,code in old_path.iter_segments():
            verts.append(vert)
            codes.append(code)
        verts.append([1,1])
        codes.append(old_path.LINETO)
        new_path = matplotlib.artist.Path(verts,codes) 
        return new_path
