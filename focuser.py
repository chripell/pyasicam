#!/usr/bin/python3

from astropy.stats import sigma_clipped_stats
from photutils import DAOStarFinder
from collections import namedtuple
import cairo
import numpy as np


FocusData = namedtuple('FocusData', 'mean p90 top std')


class Focuser:

    def __init__(self):
        self.sources = None
        self.n = 0
        self.par = {}

    def evaluate(self, data):
        mean, median, std = sigma_clipped_stats(data, sigma=3.0, iters=5)
        daofind = DAOStarFinder(fwhm=3.0, threshold=5.*std)
        self.sources = daofind(data - median)
        for col in self.sources.colnames:
            self.sources[col].info.format = "%.8g"
        if self.num() > 0:
            for p in ("sharpness", "roundness1", "roundness2"):
                self.par[p] = self.calc(p)
        return self.sources

    def num(self):
        if self.sources is not None:
            return len(self.sources)
        return 0

    def calc(self, p):
        data = self.sources.field(p)
        mean = data.mean()
        top = data.max()
        std = data.std()
        p90 = np.percentile(data, 90)
        return FocusData(mean, p90, top, std)

    def draw(self, cr, par, radius=10):
        mean = self.par[par].mean
        m_pi = 2 * np.pi
        for i in self.sources:
            if i[par] >= mean:
                cr.set_source_rgb(0, 1.0, 0)
            else:
                cr.set_source_rgb(1.0, 0, 0)
            cr.arc(i["xcentroid"], i["ycentroid"], radius, 0, m_pi)
            cr.stroke()

    def get(self, p):
        return self.par[p]
