"""
Package for Gaussian Process Optimization
=========================================

This package provides optimization functionality
for hyperparameters of covariance functions
:py:class:`pygp.covar` given. 

"""


# import scipy:
import scipy as SP
import scipy.optimize as OPT

import logging as LG


def param_dict_to_list(dict):
    """convert from param dictionary to list"""
    RV = SP.concatenate([val.flatten() for val in dict.values()])
    return RV
    pass

def param_list_to_dict(list,param_struct):
    """convert from param dictionary to list
    param_struct: structure of parameter array
    """
    RV = []
    i0= 0
    for key,val in param_struct.iteritems():
        shape = SP.array(val) 
        np = shape.prod()
        i1 = i0+np
        params = list[i0:i1].reshape(shape)
        RV.append((key,params))
        i0 = i1
    return dict(RV)


def opt_hyper(gpr,hyperparams,Ifilter=None,maxiter=100,gradcheck=False,bounds = None,optimizer=OPT.fmin_tnc,**kw_args):
    """
    Optimize hyperparemters of :py:class:`pygp.gp.basic_gp.GP` ``gpr`` starting from given hyperparameters ``hyperparams``.

    **Parameters:**

    gpr : :py:class:`pygp.gp.basic_gp`
        GP regression class
    hyperparams : {'covar':logtheta, ...}
        Dictionary filled with starting hyperparameters
        for optimization. logtheta are the CF hyperparameters.
    Ifilter : [boolean]
        Index vector, indicating which hyperparameters shall
        be optimized. For instance::

            logtheta = [1,2,3]
            Ifilter = [0,1,0]

        means that only the second entry (which equals 2 in
        this example) of logtheta will be optimized
        and the others remain untouched.

    bounds : [[min,max]]
        Array with min and max value that can be attained for any hyperparameter

    maxiter: int
        maximum number of function evaluations
    gradcheck: boolean 
        check gradients comparing the analytical gradients to their approximations
    optimizer: :py:class:`scipy.optimize`
        which scipy optimizer to use? (standard lbfgsb)

    ** argument passed onto lMl**

    priors : [:py:class:`pygp.priors`]
        non-default prior, otherwise assume
        first index amplitude, last noise, rest:lengthscales
    """

    def f(x):
        x_ = X0
        x_[Ifilter_x] = x
        
        rv =  gpr.lMl(param_list_to_dict(x_,param_struct),**kw_args)
        LG.debug("L("+str(x_)+")=="+str(rv))
        if SP.isnan(rv):
            return 1E6
        return rv
    
    def df(x):
        x_ = X0
        x_[Ifilter_x] = x
        rv =  gpr.dlMl(param_list_to_dict(x_,param_struct),**kw_args)
        #convert to list
        rv = param_dict_to_list(rv)
        LG.debug("dL("+str(x_)+")=="+str(rv))
        if SP.isnan(rv).any():
            In = SP.isnan(rv)
            rv[In] = 1E6
        return rv[Ifilter_x]

    

    #0. store parameter structure
    param_struct = dict([(name,hyperparams[name].shape) for name in hyperparams.keys()])
    
    #1. convert the dictionaries to parameter lists
    X0 = param_dict_to_list(hyperparams)
    if Ifilter is not None:
        Ifilter_x = SP.array(param_dict_to_list(Ifilter),dtype='bool')
    else:
        Ifilter_x = SP.ones(len(X0),dtype='bool')

    #2. bounds
    if bounds is not None:
        #go through all hyperparams and build bound array (flattened)
        _b = []
        for key in hyperparams.keys():
            if key in bounds.keys():
               _b.extend(bounds[key])
            else:
                _b.extend([(-SP.inf,+SP.inf)]*hyperparams[key].size)
        bounds = SP.array(_b)
        bounds = bounds[Ifilter_x]
        pass
       
        
    #2. set stating point of optimization, truncate the non-used dimensions
    x  = X0.copy()[Ifilter_x]
        
    LG.info("startparameters for opt:"+str(x))

    if gradcheck:
        LG.info("check_grad (pre) (Enter to continue):" + str(OPT.check_grad(f,df,x)))
        raw_input()
    
    LG.info("start optimization")

    #general optimizer interface
    opt_RV=optimizer(f, x, fprime=df, maxfun=maxiter,messages=False,bounds=bounds)

    #get optimized parameters out
    opt_x = X0.copy()
    opt_x[Ifilter_x] = opt_RV[0]
    opt_hyperparams = param_list_to_dict(opt_x,param_struct)
    #get the log marginal likelihood at the optimum:
    opt_lml = gpr.lMl(opt_hyperparams,**kw_args)

    if gradcheck:
        LG.info("check_grad (post) (Enter to continue):" + str(OPT.check_grad(f,df,opt_RV[0])))
        raw_input()

    LG.info("old parameters:")
    LG.info(str(hyperparams))
    LG.info("optimized parameters:")
    LG.info(str(opt_hyperparams))
    LG.info("grad:"+str(df(opt_x)))
    
    return [opt_hyperparams,opt_lml]