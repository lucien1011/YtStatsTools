import ROOT as r
import math
from array import array
import numpy as np
from rQuiet import Quiet



def drawText(outputString,xCoord = 0.15, yCoord = 0.8):
    label = r.TLatex()
    label.SetTextFont(62)
    label.SetTextColor()
    label.SetTextSize(0.04)
    label.SetTextAlign(12)
    label.DrawLatexNDC(xCoord,yCoord,outputString)
    return

def getConf(xValues,histo):
    holderGraph = r.TGraphErrors(len(xValues),array('d',xValues),array('d',[0.]*len(xValues))) 
    fitter = r.TVirtualFitter.Fitter(histo)
    fitValid = fitter.GetTFitResult().IsValid()
    fitter.SetMaxIterations(1000000)
    fitter.GetConfidenceIntervals(holderGraph,0.683)
    return holderGraph,fitValid

def saveAs(canvas,output,formatList=["png"],quiet=True,level=r.kError):
    # setPalette = SetPalette()
    # setPalette('kBird')
    for formatName in formatList:
        if quiet:
            with Quiet(r.kError):
                canvas.SaveAs(output+"."+formatName)
        else:
            canvas.SaveAs(output+"."+formatName)

def setPoissonErr(hist):
    for iXBin in range(hist.GetXaxis().GetNbins()+2):
        bkgd  = hist.GetBinContent(iXBin)
        hist.SetBinError(iXBin,getPoissonErr(bkgd))
    return 
def getPoissonErr(bkgd):
    errh = [ 1.15, 1.36, 1.53, 1.73, 1.98, 2.21, 2.42, 2.61, 2.80, 3.00, 3.16 ]
    if bkgd < 10:
        ibkgd = int(bkgd)
        err = (errh[ibkgd] + math.fmod(bkgd,1.)*(errh[ibkgd+1]-errh[ibkgd]))
        return err
    else:
        return math.sqrt(bkgd)

# { Draw the breakdown of h1, h2, ... (args = [h1, h2, ...]) per bin of 2D
#   histograms
def Draw2DPercPerBin(*args):
    def drawBox(hists, _bin, coords, col=None):
        x1, x2, y1, y2 = coords["x1"], coords["x2"], coords["y1"], coords["y2"]
        if col==None:
            binVals = [hist.GetBinContent(*_bin) for hist in hists]
        else:
            binVals = hists
        total = sum(binVals)
        if total == 0.:
            return

        lastx = x1
        for k, hist in enumerate(hists):
            if col==None:
                box.SetLineColor(hist.GetLineColor())
                box.SetFillColor(hist.GetFillColor())
            else:
                box.SetLineColor(col[k])
                box.SetFillColor(col[k])

            thisx = x1 + (x2-x1)*sum(binVals[:k+1])/float(total)
            box.DrawBox(lastx, y1, thisx, y2)
            lastx = thisx
        return

    hTemp = args[0].Clone()
    args[0].Draw("axis") # draw axis labels

    # Projections
    hProjX  = [h.ProjectionX() for h in args]
    hProjY  = [h.ProjectionY() for h in args]
    hProjXY = [h.Integral() for h in hProjX]

    box = r.TBox()
    for i in range(1, hTemp.GetNbinsX()+1):
        x1 = hTemp.GetXaxis().GetBinLowEdge(i)
        x2 = hTemp.GetXaxis().GetBinUpEdge(i)
        coords = {"x1": x1, "x2": x2}
        for j in range(1, hTemp.GetNbinsY()+1):
            y1 = hTemp.GetYaxis().GetBinLowEdge(j)
            y2 = hTemp.GetYaxis().GetBinUpEdge(j)
            coords["y1"] = y1
            coords["y2"] = y2
            drawBox(args, [i,j], coords)
        #<--j

        # x Projection
        coords["y1"] += 2.*(y2-y1)
        coords["y2"] += 2.*(y2-y1)
        drawBox(hProjX, [i], coords)
    #<--i

    # y Projections
    coords["x1"] += 1.5*(x2-x1)
    coords["x2"] += 1.5*(x2-x1)
    for j in range(1, hTemp.GetNbinsY()+1):
        y1 = hTemp.GetYaxis().GetBinLowEdge(j)
        y2 = hTemp.GetYaxis().GetBinUpEdge(j)
        coords["y1"] = y1
        coords["y2"] = y2
        drawBox(hProjY, [j], coords)

    coords["y1"] += 2.*(y2-y1)
    coords["y2"] += 2.*(y2-y1)
    col = [h.GetFillColor() for h in hProjX]
    drawBox(hProjXY, [1], coords, col=col)

    # Pseudo legend
    text = r.TText()
    text.SetTextAngle(-90)
    text.SetTextFont(42)
    text.SetTextSize(0.03)
    names = [h.GetName() for h in args]
    x1, x2 = coords["x1"], coords["x2"]
    y1 = -0.1
    for i, name in enumerate(names):
        if i==0:
            text.SetTextAlign(11)
        elif i==len(names)-1:
            text.SetTextAlign(13)
        else:
            text.SetTextAlign(12)

        xpos = x1 + i*(x2-x1)/float(len(names)-1)
        text.DrawText(xpos, y1, name)

    args[0].Draw("axissame") # Draw tick marks ontop of rectangles
    return
# }

# { Project 2D yields of HT vs. cat onto HT, nJet or bJet
#   Error is taken as the sqrt(sum(errors**2))
def projectHT(hist2D):
    histHT = hist2D.ProjectionX(hist2D.GetName()+"_HT")
    histHT.SetDirectory(0)
    return histHT

def projectNJet(hist2D):
    # Count number of bins
    bins = []
    for j in range(1, hist2D.GetNbinsY()+1):
        binLabel = hist2D.GetYaxis().GetBinLabel(j)
        try:
            if binLabel.split("_")[1] not in bins:
                bins.append(binLabel.split("_")[1])
        except IndexError:
            print "Error: Y-axis bin label in the wrong format, e.g. should be eq0b_eq1j"
            exit()

    # Create hist for projection
    histNJet = r.TH1D(hist2D.GetName()+"_nJet", "", len(bins), 0, len(bins))
    histNJet.SetDirectory(0)
    histNJet.Sumw2()
    histNJet.GetYaxis().SetTitle(hist2D.GetZaxis().GetTitle())
    for i in range(1, histNJet.GetNbinsX()+1):
        histNJet.GetXaxis().SetBinLabel(i, bins[i-1])

        integral = 0.0
        error2   = 0.0
        for j in range(1, hist2D.GetNbinsY()+1):
            binLabel = hist2D.GetYaxis().GetBinLabel(j)
            if binLabel.split("_")[1] == bins[i-1]:
                tempError    = r.Double(0.)
                tempIntegral = hist2D.IntegralAndError(0, hist2D.GetNbinsX()+1, j, j, tempError)
                integral += tempIntegral
                error2   += tempError**2
        histNJet.SetBinContent(i, integral)
        histNJet.SetBinError  (i, math.sqrt(error2))
    return histNJet

def projectBJet(hist2D):
    # Count number of bins
    bins = []
    for j in range(1, hist2D.GetNbinsY()+1):
        binLabel = hist2D.GetYaxis().GetBinLabel(j)
        try:
            if binLabel.split("_")[0] not in bins:
                bins.append(binLabel.split("_")[0])
        except IndexError:
            print "Error: Y-axis bin label in the wrong format, e.g. should be eq0b_eq1j"
            exit()

    # Create hist for projection
    histBJet = r.TH1D(hist2D.GetName()+"_bJet", "", len(bins), 0, len(bins))
    histBJet.SetDirectory(0)
    histBJet.Sumw2()
    histBJet.GetYaxis().SetTitle(hist2D.GetZaxis().GetTitle())
    for i in range(1, histBJet.GetNbinsX()+1):
        histBJet.GetXaxis().SetBinLabel(i, bins[i-1])

        integral = 0.0
        error2   = 0.0
        for j in range(1, hist2D.GetNbinsY()+1):
            binLabel = hist2D.GetYaxis().GetBinLabel(j)
            if binLabel.split("_")[0] == bins[i-1]:
                tempError    = r.Double(0.)
                tempIntegral = hist2D.IntegralAndError(0, hist2D.GetNbinsX()+1, j, j, tempError)
                integral += tempIntegral
                error2   += tempError**2
        histBJet.SetBinContent(i, integral)
        histBJet.SetBinError  (i, math.sqrt(error2))
    return histBJet
# }

def Draw2DBreakdownPerBin(*args):
    """
    Draw the breakdown of h1, h2, ... (args = [h1, h2, ...]) per bin of 2D
    histograms. Includes x and y projections, a total bin and a legend.
    Colours are taken from the histograms via "GetFillColor" and names via
    "GetName".
    """
    box = r.TBox()
    def drawBox(hists, _bin, coords, col=None):
        x1, x2, y1, y2 = coords["x1"], coords["x2"], coords["y1"], coords["y2"]
        if col == None:
            binVals = [hist.GetBinContent(*_bin) for hist in hists]
        else:
            binVals = hists
        total = sum(binVals)
        if total == 0.:
            return

        prev_x = x1
        for k, hist in enumerate(hists):
            if col == None:
                box.SetLineColor(hist.GetLineColor())
                box.SetFillColor(hist.GetFillColor())
            else:
                box.SetLineColor(col[k])
                box.SetFillColor(col[k])

            curr_x = x1 + (x2-x1)*sum(binVals[:k+1])/float(total)
            box.DrawBox(prev_x, y1, curr_x, y2)
            prev_x = curr_cx
        return

    # Template histogram (used for binning)
    hTempl = args[0].Clone()
    args[0].Draw("axis")

    # Projections
    hProjX  = [h.ProjectionX() for h in args]
    hProjY  = [h.ProjectionY() for h in args]
    hProjXY = [h.Integral() for h in hProjX]

    for i in range(1, hTempl.GetNbinsX()+1):
        x1 = hTempl.GetXaxis().GetBinLowEdge(i)
        x2 = hTempl.GetXaxis().GetBinUpEdge(i)
        coords = dict(x1=x1, x2=x2)
        for j in range(1, hTempl.stGetNbinsY()+1):
            y1 = hTempl.GetYaxis().GetBinLowEdge(j)
            y2 = hTempl.GetYaxis().GetBinUpEdge(j)
            coords["y1"] = y1
            coords["y2"] = y2
            drawBox(args, [i,j], coords)
        #<--j

        # X projection
        coords["y1"] += 2.*(y2-y1)
        coords["y2"] += 2.*(y2-y1)
        drawBox(hProjX, [i], coords)
    #<--i

    # Y projections
    coords["x1"] += 1.5*(x2-x1)
    coords["x2"] += 1.5*(x2-x1)
    for j in range(1, hTempl.GetNbinsY()+1):
        y1 = hTempl.GetYaxis().GetBinLowEdge(j)
        y2 = hTempl.GetYaxis().GetBinUpEdge(j)
        coords["y1"] = y1
        coords["y2"] = y2
        drawBox(hProjY, [j], coords)
    #<--j

    # Total
    coords["y1"] += 2.*(y2-y1)
    coords["y2"] += 2.*(y2-y1)
    col = [h.GetFillColor() for h in hProjX]
    drawBox(hProjXY, [1], coords, col=col)

    # Pseudo legend
    text = r.TLatex()
    text.SetTextAngle(-90)
    text.SetTextFont(42)
    text.SetTextSize(hTempl.GetXaxis().GetLabelSize())
    text.SetTextAlign(12)
    text.SetTextColor(r.kWhite)
    names = [h.GetName() for h in args]
    x1, x2 = coords["x1"], coords["x2"]
    y1 = -0.5*abs(coords["y2"]-coords["y1"])
    y2 = 7*y1
    drawBox([1]*len(names), [1], dict(x1=x1,x2=x2,y1=y1,y2=y2), col=col)
    for i, name in enumerate(names):
        xpos = x1 + (i+0.5)*(x2-x1)/float(len(names))
        text.DrawLatex(xpos, y1, name)

    args[0].Draw("axissame")
    return


class SetPalette():

    def __init__(self,ncontours=999,alpha = 1,style=r.gStyle):
        self._palettes  = {}
        self._ncontours = ncontours
        self._alpha = alpha
        self._style = style

    def __call__(self,name=""):
        if name in self._palettes:
            self._style.SetPalette(len(self._palettes[name]),self._palettes[name])
        else:
            self._setPalette(name)

    def __call__(self,name = ""):
        if type(name) == int:
            self._style.SetPalette(name)
            self._style.SetNumberContours(self._ncontours)
        elif type(name) == str:
            if name in self._palettes:
                self._style.SetPalette(len(self._palettes[name]),self._palettes[name])
            else:
                self._setPalette(name)
        else:
            raise AttributeError, "Need string or int"
    def _setPalette(self,name):
        """Set a color palette from a given RGB list
        stops, red, green and blue should all be lists of the same length
        see set_decent_colors for an example"""

        if name == "gray" or name == "grayscale":
            stops = [0.00, 0.34, 0.61, 0.84, 1.00]
            red   = [1.00, 0.84, 0.61, 0.34, 0.00]
            green = [1.00, 0.84, 0.61, 0.34, 0.00]
            blue  = [1.00, 0.84, 0.61, 0.34, 0.00]
        # elif name == "frenchFlag":
        #     stops = [0.00, 0.5, 0.99,1.00]
        #     red   = [0.00, 1.00, 1.00,0.70]
        #     green = [0.00, 1.00, 0.00,0.80]
        #     blue  = [1.00, 1.00, 0.00,0.80]
        elif name == "frenchFlag":
            stops = [0.00, 0.5, 1.00]
            red   = [0.00, 1.00, 1.00]
            green = [0.00, 1.00, 0.00]
            blue  = [1.00, 1.00, 0.00]
        elif name == "kBird":
            stops = [0.0000, 0.1250, 0.2500, 0.3750, 0.5000, 0.6250, 0.7500, 0.8750, 1.0000]
            red   = [0.2082, 0.0592, 0.0780, 0.0232, 0.1802, 0.5301, 0.8186, 0.9956, 0.9764]
            green = [0.1664, 0.3599, 0.5041, 0.6419, 0.7178, 0.7492, 0.7328, 0.7862, 0.9832]
            blue  = [0.5293, 0.8684, 0.8385, 0.7914, 0.6425, 0.4662, 0.3499, 0.1968, 0.0539]
        elif name == "watermelon":
            stops = [0.0000, 0.1250, 0.2500, 0.3750, 0.5000, 0.6250, 0.7500, 0.8750, 1.0000]
            red   = [ 19./255., 42./255., 64./255.,  88./255., 118./255., 147./255., 175./255., 187./255., 205./255.]
            green = [ 19./255., 55./255., 89./255., 125./255., 154./255., 169./255., 161./255., 129./255.,  70./255.]
            blue  = [ 19./255., 32./255., 47./255.,  70./255., 100./255., 128./255., 145./255., 130./255.,  75./255.]
        elif name == "pulls" :
            nStop = 12
            nc = nStop*1.
            stops = [0./nc, 1./nc, 1./nc, 5./nc, 5./nc, 7./nc, 7./nc, 11./nc, 11./nc, 12./nc]
            red   = [ 0.00,  0.00,  0.50,  0.90,  0.95,  0.95,  1.00,   1.00,   1.00,   1.00]
            green = [ 0.00,  0.00,  0.50,  0.90,  0.95,  0.95,  0.90,   0.50,   0.00,   0.00]
            blue  = [ 1.00,  1.00,  1.00,  1.00,  0.95,  0.95,  0.90,   0.50,   0.00,   0.00]
        elif name == "positive_pulls" :
            nStop = 10
            nc = nStop*1.
            stops = [0.00, 1.00]
            red   = [1.00, 1.00]
            green = [1.00, 0.00]
            blue  = [1.00, 0.00]
        elif name == "exclusion95" :
            stops = [0.00, 0.34, 0.61, 0.84, 0.95, 0.95, 1.00]
            red   = [0.00, 0.00, 0.87, 1.00, 0.51, 0.00, 0.00]
            green = [0.00, 0.81, 1.00, 0.20, 0.00, 0.00, 0.00]
            blue  = [0.51, 1.00, 0.12, 0.00, 0.00, 0.00, 0.00]
        elif name == "exclusion05" :
            stops = [0.00, 0.05, 0.05, 0.34, 0.61, 0.84, 1.00]
            red   = [0.00, 0.00, 0.00, 0.00, 0.87, 1.00, 0.51]
            green = [0.00, 0.00, 0.00, 0.81, 1.00, 0.20, 0.00]
            blue  = [0.00, 0.00, 0.51, 1.00, 0.12, 0.00, 0.00]
        elif name == "":
            # default palette, looks cool
            stops = [0.00, 0.34, 0.61, 0.84, 1.00]
            red   = [0.00, 0.00, 0.87, 1.00, 0.51]
            green = [0.00, 0.81, 1.00, 0.20, 0.00]
            blue  = [0.51, 1.00, 0.12, 0.00, 0.00]
        else:
            raise AttributeError, "No such name '{0}'".format(str(name))
            pass

        stops = array('d', stops)
        red   = array('d', red)
        green = array('d', green)
        blue  = array('d', blue)

        npoints = len(stops)
        ind     = r.TColor.CreateGradientColorTable(npoints, stops, red, green, blue, self._ncontours,self._alpha)
        self._style.SetNumberContours(self._ncontours)
        self._palettes[name] = array('i',[x+ind for x in range(self._ncontours)])

# testPalette = SetPalette()
# testPalette("frenchFlag")
# testPalette(54)
