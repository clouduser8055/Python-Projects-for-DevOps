l = [{"one":1, "name":"anuj", "surname": 1},{"two":2, "name":"rachisdft", "surname": 2}, {"three": 3, "name":"samarth", "surname": 3}]
l.sort(key = lambda numbers:numbers["surname"], reverse=True)
print(l)