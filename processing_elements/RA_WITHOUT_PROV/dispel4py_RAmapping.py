import json
import random
import os
import matplotlib.pyplot as plt 
import numpy
#try:
#    from mpl_toolkits.basemap import Basemap
#except:
os.environ['PROJ_LIB']="/anaconda3/envs/mypython3/share/proj"
from mpl_toolkits.basemap import Basemap
from mpl_toolkits.axes_grid1 import make_axes_locatable
from dispel4py.core import GenericPE
from dispel4py.base import ConsumerPE
from dispel4py.workflow_graph import WorkflowGraph


def plot_single(f,ax,variable='PGV',kind='data',source=None,bounds=None,xtitle=None,ytitle=None,vmin=None,vmax=None):

    lon= [x['properties']['geometry']['coordinates'][1]for x in source["features"]]
    lat= [x['properties']['geometry']['coordinates'][0]for x in source["features"]]
    values=[x['properties'][kind][variable] for x in source["features"]]
    print("max lat %s, min lat %s, lat %s" %(max(lat), min(lat), lat))
    a=plt.axes(ax)
    if not bounds:
        dlat=(max(lat)-min(lat))*.3
        dlon=(max(lon)-min(lon))*.3
        minlat=min(lat)-dlat
        maxlat=max(lat)+dlat
        minlon=min(lon)-dlon
        maxlon=max(lon)+dlon
    else:
        minlat=bound[2]
        maxlat=bound[3]
        minlon=bound[0]
        maxlon=bound[1]
    if vmin is None:
        vmin=min(values)
    if vmax is None:
        vmax=max(values)
    print("lat %s, lon %s, max(lat) %s, min(lat) %s,dlat %s, dlon %s,minlat %s, maxlat %s, minlon %s, maxlon %s" %(lat,lon,max(lat),min(lat),dlat,dlon,minlat,maxlat, minlon, maxlon))
    m = Basemap(projection='merc', resolution='i',llcrnrlat=minlat, urcrnrlat=maxlat, llcrnrlon=minlon, urcrnrlon=maxlon)
    #m = Basemap(epsg="3395", resolution='i',
    #        llcrnrlat=minlat, urcrnrlat=maxlat,
    #        llcrnrlon=minlon, urcrnrlon=maxlon)
    
    x,y=m(lon,lat)
    if kind == 'difference' or kind == 'relative_difference':
        cmap='seismic'
    else:
        cmap='hot_r'
    scat=m.scatter(x,y, alpha=1, edgecolors='k',cmap=cmap,c=values,vmin=vmin,vmax=vmax)
    
    #m.shadedrelief()
    m.arcgisimage(service = "World_Shaded_Relief", xpixels = 400)
    #m.drawcoastlines()
    parallels = [round(minlat+.1e-3,2),round(maxlat-.1e-1,2)]
    
    if xtitle:
        plt.title(xtitle,fontsize=20)
    if ytitle:
        m.drawparallels(parallels,labels=[True,False,False,False])
        plt.ylabel(ytitle,fontsize=18)
    else:
        m.drawparallels(parallels,labels=[False,False,False,False])
    
    if variable == "PSA_3.0Hz":
        # labels = [left,right,top,bottom]
        meridians = [round(minlon+.1e-3,2),round(maxlon-.1e-1,2)]
        m.drawmeridians(meridians,labels=[False,False,False,True],rotation='vertical')
        unitlabel=r'$[m/s^2]$'
    elif variable[2] == 'A':
        unitlabel=r'$[m/s^2]$'
    elif variable[2] == 'V':
        unitlabel=r'$[m/s]$'
    elif variable[2] == 'D':
        unitlabel=r'$[m]$'
    
    
    divider = make_axes_locatable(a)
    cax = divider.append_axes('right', size='5%', pad=0.05)
    if kind == 'difference':
        f.colorbar(scat, cax=cax, orientation='vertical',label=unitlabel)
    else:
        f.colorbar(scat, cax=cax, orientation='vertical')
        
def get_values_extremes(source=None,variable='PGV'):
    kind='data'
    values=[x['properties'][kind][variable] for x in source["features"]]
    min_variable=min(values)
    max_variable=max(values)
    kind='synt'
    values=[x['properties'][kind][variable] for x in source["features"]]
    min_variable=min(min(values),min_variable)
    max_variable=max(max(values),max_variable)
    kind='difference'
    values=[x['properties'][kind][variable] for x in source["features"]]
    max_difference=max(numpy.abs(values))
    
    return min_variable,max_variable,max_difference



class StreamProducer(GenericPE):
    """
    PE reading the JSON input file and generating one output per component of
    the input files. Will write to different output channels depending on the
    chosen misfit.
    """
    def __init__(self):
        GenericPE.__init__(self)
        self._add_output("output_max")
        self._add_output("output_mean")

    def _process(self, inputs):
         data_max={}
         data_mean={}
         data_max["features"]=[]
         data_mean["features"]=[]
         for filename in os.listdir(gm_path):
             if filename.endswith("_max.json"):
                 with open(gm_path+"/"+filename, "r") as read_file:
                     data_station = json.load(read_file)
                     data_max["features"].append(data_station)
             else:
                 with open(gm_path+"/"+filename, "r") as read_file:
                     try:
                         data_station = json.load(read_file)
                         data_mean["features"].append(data_station)
                     except:
                         print('error loading ',gm_path+"/"+filename)
         self.write('output_mean', data_mean)
         self.write('output_max', data_max)


class PlotMap(ConsumerPE):
    def __init__(self, label):
        ConsumerPE.__init__(self)
        self.label = label
        self._add_output("plot")

    def _process(self, data):
        data_source = data
        fig, axes = plt.subplots(6, 3, sharex='col', sharey='row')
        fig.set_size_inches([10,20])
        kinds=['data', 'synt', 'difference']
        variables=['PGA','PGV','PGD','PSA_0.3Hz','PSA_1.0Hz','PSA_3.0Hz']
        extremes={}
        for v in variables:
            vmin,vmax,vmax_diff=get_values_extremes(data_source,variable=v)
            extremes[v]={'max':vmax,'min':vmin,'mindiff':-vmax_diff,'maxdiff':vmax_diff}
        
        for i,k in enumerate(kinds):
            for j,v in enumerate(variables):
                ax=axes[:,i]
                if k == 'difference' or k == 'relative_difference':
                    vmin=extremes[v]['mindiff']
                    vmax=extremes[v]['maxdiff']
                else:
                    vmin=extremes[v]['min']
                    vmax=extremes[v]['max']
                    
                if j == 0:
                    xtitle=k
                else:
                    xtitle=None
                
                if i == 0:
                    ytitle=v
                else:
                    ytitle=None
                    
                plot_single(fig, ax[j] ,v,k,source=data_source,xtitle=xtitle,ytitle=ytitle,vmin=vmin,vmax=vmax)
            
        savefig=gm_path+"/RAMap_"+self.label+".png"
        fig.savefig(savefig)
        self.write('plot',savefig,location=savefig,format="image/png")


gm_path=os.environ['OUTPUT']
producer_PE=StreamProducer()
producer_PE.name="streamProducer"
plotMax=PlotMap("max")
plotMean=PlotMap("mean")

graph = WorkflowGraph()
graph.connect(producer_PE, "output_max", plotMax, "input")
graph.connect(producer_PE, "output_mean", plotMean, "input")

