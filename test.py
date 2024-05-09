a = (x for x in range(100) if x > 100)

print(a)
print(bool(a))
print(len(a))
for x in a:
    print(x)
print('=============================')
a = (x for x in range(100))

print(a)
print(bool(a))
print(len(a))
for x in a:
    print(x)