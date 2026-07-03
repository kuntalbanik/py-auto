#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class Cart:
    def __init__(self, basket1, basket2, basket3):
        self.basket1 = basket1
        self.basket2 = basket2
        self.basket3 = basket3
    
    def __len__(self):
        return len(self.basket1) + len(self.basket2) + len(self.basket3)
    
    def __str__(self):
        print("Total number of cart")
        return str(self.__len__())

crt = Cart(["apple", "banana"], ["orange", "grape"], ["milk", "cheese"])
print(len(crt))
