from pathlib import Path
from numpy import ones
from os import devnull
from matplotlib.pyplot import figure,draw,pause
from matplotlib.colors import LogNorm
import matplotlib.animation as anim
#
from astrometry_azel.plots import plotazel

def plotjointazel(waz,wel,rows,cols,wR,wC,asifn=None,projalt=None):

    ttxt = 'Projected to {} km\n'.format(projalt/1e3)
    fg,axa,axe = plotazel(waz,wel,x=wC,y=wR,makeplot='show',ttxt=ttxt)

    overlayrowcol(axa,rows,cols)
    overlayrowcol(axe,rows,cols)

    if asifn:
        pfn = Path(asifn).expanduser().with_suffix('.png')
        fg.savefig(str(pfn),bbox_inches='tight',dpi=100)

def overlayrowcol(ax,rows,cols):
    """
    plot FOV outline onto image via the existing axis "ax"

    inputs:
    ax: existing plot axis to overlay lines outlining FOV
    rows,cols: indices to plot

    wants a list of len(4) list x Npixel
    that is, like a 3D array Ncam x Nside x Npixelonside
    but using lists since cameras have different resolutions
    and may be rectangular.
    """
    colors = ('g','r','m','y','c')

    if rows is not None and cols is not None:
        for row,col,color in zip(rows,cols,colors): #for c in cam
            if isinstance(row,list):
                for r,c in zip(row,col): # for l in lines
                    ax.plot(c,r,color=color,linewidth=2,alpha=0.5)
            else: #single camera
                ax.plot(col,row,color='g',linewidth=2,alpha=0.5)

def plotthemis(imgs,T,site='',treq=None,ofn=None,rows=None,cols=None,ext=None):
    """
    rows,cols expect lines to be along rows Nlines x len(line)
    list of 1-D arrays or 2-D array
    """
    if ofn:
        ofn = Path(ofn).expanduser()
        write=True
    else:
        ofn = devnull
        write=False

    Writer = anim.writers['ffmpeg']
    writer = Writer(fps=5,
                    metadata=dict(artist='Michael Hirsch'),
                    codec='ffv1')
    """
    NOTE: codec must be compatible with file container type.
    ffv1: avi, mkv
    mpeg4: mp4
    """

    fg = figure()
    ax = fg.gca()

    hi = ax.imshow(imgs[0],cmap='gray',origin='lower',norm=LogNorm(),
                   interpolation='none',extent=ext)
    ttxt = 'Themis ASI {} FOV vs. HST0,HST1: green,red '.format(site)
    ht = ax.set_title(ttxt,color='g')
    ax.set_xlabel('x-pixels')
    ax.set_ylabel('y-pixels')
    ax.autoscale(True,tight=True)
    ax.grid(False)
#%% plot narrow FOV outline
    overlayrowcol(ax,rows,cols)
#%% play video
    if treq: #maybe you loaded a lot of video but only want to play small parts of it.
        tgood = (treq[0]<=T) & (T<=treq[1])
    else:
        tgood = ones(T.size).astype(bool)


    with writer.saving(fg, str(ofn),150):
        for I,t in zip(imgs[tgood,...],T[tgood]):
            hi.set_data(I)
            ht.set_text(ttxt + str(t))
            draw(),pause(0.01)
            if write: writer.grab_frame(facecolor='k')

#        if odir:
#            fg.savefig(str(odir/'Themis_{}_{}.png'.format(site,t.timestamp())),bbox_inches='tight',facecolor='k',dpi=150)

