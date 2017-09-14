##  Colorspace conversions library
import sys
import math

def Rgb2Hsl (rgbtuple):
    # H, S, L will be in [0.0 ... 1.0]
    r, g, b = rgbtuple
    rScaled = r#/255.0
    gScaled = g#/255.0
    bScaled = b#/255.0
    rgbMin = min (rScaled, gScaled, bScaled)    # Min RGB value
    rgbMax = max (rScaled, gScaled, bScaled)    # Max RGB value
    deltaRgb = rgbMax - rgbMin                  # Delta RGB value
    L = (rgbMax + rgbMin) / 2.0
    if (deltaRgb == 0.0):   # This is a gray, no chroma.
       H = 0.0
       S = 0.0              # Done !
    else:                   # Chromatic data...
        if (L < 0.5):
            S = deltaRgb / (rgbMax + rgbMin)
        else:
            S = deltaRgb / (2.0 - rgbMax - rgbMin)
        deltaR = (((rgbMax - rScaled)/6.0) + (deltaRgb/2.0)) / deltaRgb
        deltaG = (((rgbMax - gScaled)/6.0) + (deltaRgb/2.0)) / deltaRgb
        deltaB = (((rgbMax - bScaled)/6.0) + (deltaRgb/2.0)) / deltaRgb
        if   (rScaled == rgbMax): 
            H = deltaB - deltaG
        elif (gScaled == rgbMax): 
            H = (1.0/3.0) + deltaR - deltaB
        elif (bScaled == rgbMax): 
            H = (2.0/3.0) + deltaG - deltaR
        H = H % 1.0
    return (H, S, L)


def Hsl2Rgb (hsltuple):

    def HslHue2Rgb (v1, v2, vH):
       if (vH < 0.0):    vH += 1.0
       if (vH > 1.0):    vH -= 1.0
       if ((6.0 * vH) < 1.0):    return (v1 + (v2 - v1) * 6.0 * vH)
       if ((2.0 * vH) < 1.0):    return (v2)
       if ((3.0 * vH) < 2.0):    return (v1 + (v2 - v1) * ((2.0/3.0) - vH) * 6.0)
       return v1

    # H, S, L in [0.0 .. 1.0]
    H, S, L = hsltuple
    if (S == 0.0):          # RGB grayscale
       r = L * 255.0        # R, G, B in [0 .. 255]
       g = L * 255.0
       b = L * 255.0
    else:
        if (L < 0.5): 
            var_2 = L * (1.0 + S)
        else:           
            var_2 = (L + S) - (S * L)
        var_1 = (2.0 * L) - var_2
        r = HslHue2Rgb (var_1, var_2, H + (1.0/3.0)) # *  255
        g = HslHue2Rgb (var_1, var_2, H ) # *  255
        b = HslHue2Rgb (var_1, var_2, H - (1.0/3.0)) # *  255
    return (r, g, b)
    #r = int (r + 0.5)
    #g = int (g + 0.5)
    #b = int (b + 0.5)
    #return (r, g, b)


def Rgb2Hsv (rgbtuple):
    # H, S, V will be in [0.0 ... 1.0]
    r, g, b = rgbtuple
    r = r / 255.0
    g = g / 255.0
    b = b / 255.0
    minRgb = min (r, g, b)
    maxRgb = max (r, g, b)
    deltaRgb = maxRgb - minRgb
    v = maxRgb
    if (deltaRgb == 0):     # This is a gray, no chroma...
       h = 0.0
       s = 0.0
    else:                   # Chromatic data
        s = deltaRgb / maxRgb
        del_R = (((maxRgb - r) / 6.0) + (deltaRgb / 2.0)) / deltaRgb
        del_G = (((maxRgb - g) / 6.0) + (deltaRgb / 2.0)) / deltaRgb
        del_B = (((maxRgb - b) / 6.0) + (deltaRgb / 2.0)) / deltaRgb

        if   (r == maxRgb):
            h = del_B - del_G
        elif (g == maxRgb):
            h = (1.0 / 3.0) + del_R - del_B
        elif (b == maxRgb):
            h = (2.0 / 3.0) + del_G - del_R
        h = h % 1.0
    return (h, s, v)


def Hsv2Rgb (hsvtuple):
    h, s, v = hsvtuple
    if (s == 0.0):
       r = v * 255.0
       g = v * 255.0
       b = v * 255.0
    else:
        h = h * 6.0
        I = int (h)          # floor function
        F = h - I
        P = v * (1.0 - s)
        Q = v * (1.0 - s * F)
        T = v * (1.0 - s * (1.0 - F))
        if   (I == 4):
            r = T
            g = P
            b = v
        elif (I == 5):
            r = v
            g = P
            b = Q
        elif (I == 0):
            r = v
            g = T
            b = P
        elif (I == 1):
            r = Q
            g = v
            b = P
        elif (I == 2):
            r = P
            g = v
            b = T
        elif (I == 3):
            r = P
            g = Q
            b = v
        r = int ((r * 255.0) + 0.5)
        g = int ((g * 255.0) + 0.5)
        b = int ((b * 255.0) + 0.5)
    return (r, g, b)

