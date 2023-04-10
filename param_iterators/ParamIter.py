# MIT License
 
# Copyright (c) 2023 Advanced Micro Devices, Inc.
 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from abc import abstractmethod

from logger import logger
from param_iterators.IterPublisher import IterPublisher
from param_iterators.IterSubscriber import IterSubscriber


class ParamIter(IterPublisher, IterSubscriber):
    """Iterator Super class for different types of Iterators

    Iterators should be publishers and subscribers.
    When Update gets called, they should iterate and if there are subscribers,
    they should notify the subscribers to iterate and reset it's count unless the subscribers
    are all finished iterating(raise StopIteration)

    Methods:
        update()->None: Updates the count of iterator, if count is greater than max count,
            then it notifies subscribers, if no subscribers raise StopIteration
        resetCount(resetSubs)->None: Resets the iterator to zero, if resetSubs is true, then it also resets
            all subscribers
        current()->Object: gets the current value of the iterator
    """

    def __init__(self, subscribers=[], controller=None):
        self.controller = controller
        if self.controller:
            # The controller should set the current value immediately
            # for example if psm is set to -11, we should set the value on the controller before doing anything else
            self.controller.update(self.current())
        super().__init__(subscribers)

    def update(self):
        logger.debug("Param Iter Update")
        self.count += 1
        try:
            self.current()
            if self.controller:
                logger.debug("A controller exists, updating controller: {}".format(self.controller))
                self.controller.update(self.current())
        except (StopIteration, IndexError):
            logger.debug("Exception Raised, notifying subscribers")
            notified = self.notify()
            if notified:
                logger.debug("Subscribers notified, reset count")
                self.count = 0
                self.resetCount()
            else:
                logger.debug("No Subscribers, raise exception")
                raise StopIteration

    def resetCount(self, resetSubs=False):
        if not resetSubs:
            return
        for sub in self.subscribers:
            if isinstance(sub, ParamIter):
                sub.resetCount()

    @abstractmethod
    def current(self):
        pass
