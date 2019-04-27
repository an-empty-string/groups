Having trouble with really small finite groups? This is the tool for you. Here
are some examples.

# Examples

## Construct Z / 5Z

```
z5 = Group.integers_mod(5)
```

## Construct an automorphism group

```
z3 = Group.integers_mod(3)
aut_z3 = z3.automorphism_group()
```

## Show that S2 and Z / 2Z are isomorphic

```
s2 = Group.symmetric_group(2)
z2 = Group.integers_mod(2)
print(next(z2.isomorphisms_to(s2)))
```

## Construct the Klein four-group and show it is abelian

```
z2 = Group.integers_mod(2)
v4 = z2 * z2
v4.abelian()  # True
print(list(v4))  # [(0, 1) in Z2*Z2, (1, 0) in Z2*Z2,
                 #  (0, 0) in Z2*Z2, (1, 1) in Z2*Z2]
```
