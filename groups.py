import itertools


class GroupElement:
    def __init__(self, group, token):
        self.group = group
        self.token = token

    def order(self):
        if self == self.group.identity:
            return 1

        c = 1
        k = self
        while True:
            c += 1
            k *= self
            if k == self.group.identity:
                return c

    def __mul__(self, other):
        if other in self.group:
            return self.group.operation(self, other)

    def __add__(self, other):
        return self * other

    def __eq__(self, other):
        return self.group == other.group and self.token == other.token

    def __str__(self):
        return "{} in {}".format(self.token, self.group.name)

    def __repr__(self):
        return str(self)

    def __invert__(self):
        return self.group.inverse(self)

    def __neg__(self):
        return ~self

    def __lt__(self, other):
        return self.group.compare(self, other) < 0

    def __gt__(self, other):
        return self.group.compare(self, other) > 0

    def __hash__(self):
        return hash(self.token)

    def __xor__(self, n):
        el = self
        if n < 0:
            el = -self

        k = self.group.identity
        for i in range(abs(n)):
            k *= el

        return k


class Group:
    name = None
    _elements = set()
    _identity = None

    def __contains__(self, el):
        return el.token in self._elements and el.group == self

    def __iter__(self):
        for tok in self._elements:
            yield GroupElement(self, tok)

    def __getitem__(self, token):
        assert token in self._elements

        return GroupElement(self, token)

    def __mul__(self, other):
        assert isinstance(other, Group)

        # direct product time
        new_els = {(i, j) for i in self._elements for j in other._elements}
        new_identity = (self._identity, other._identity)

        def new_operation(group, a, b):
            return group[(
                self.operation(self[a.token[0]], self[b.token[0]]).token,
                other.operation(other[a.token[1]], other[b.token[1]]).token
            )]

        def new_inverse(group, a):
            return group[(
                self.inverse(self[a.token[0]]).token,
                other.inverse(other[a.token[1]]).token
            )]

        def new_compare(group, a, b):
            r1 = self.compare(self[a.token[0]], self[b.token[0]])
            if r1 != 0:
                return r1

            return other.compare(other[a.token[1]], other[b.token[1]])

        return type("DirectProduct", (Group,), {
            "name": "{}*{}".format(self.name, other.name),
            "_elements": new_els,
            "_identity": new_identity,
            "operation": new_operation,
            "inverse": new_inverse,
            "compare": new_compare,
        })()

    def __len__(self):
        return len(self._elements)

    def __eq__(self, other):
        return self.name == other.name

    def abelian(self):
        for g in self:
            for h in self:
                if g * h != h * g:
                    return False

        return True

    def center(self):
        els = set()

        for g in self:
            for h in self:
                # if g commutes with every element in the group, it is
                # in the center of the group
                if g * h != h * g:
                    break
            else:
                els.add(g)

        return els

    def homomorphisms_to(self, other):
        k = itertools.product(range(len(other)), repeat=len(self))
        self_els = list(self)
        other_els = list(other)

        for i in k:
            candidate_rule = {self_els[j].token: other_els[i[j]].token for j in range(len(i))}
            candidate = Function(self, other, candidate_rule)

            if candidate.is_homomorphism():
                yield candidate

    def isomorphisms_to(self, other):
        for h in self.homomorphisms_to(other):
            if h.bijective():
                yield h

    @classmethod
    def integers_mod(cls, n):
        def operation(group, a, b):
            return group[(a.token + b.token) % n]

        def compare(group, a, b):
            return a.token - b.token

        return type("IntegersMod", (Group,), {
            "name": "Z{}".format(n),
            "_elements": set(range(n)),
            "_identity": 0,
            "operation": operation,
            "compare": compare
        })()

    @classmethod
    def symmetric_group(cls, n):
        def operation(group, a, b):
            return group[(a.token * b.token)]

        permutes = Group.integers_mod(n)

        all_permutation = [
            Function(permutes, permutes, {
                k: permutation[k] for k in range(n)
            }) for permutation in itertools.permutations(range(n))
        ]

        def cycle(group, c):
            full_range = set(range(n))
            not_changed = full_range.difference(set(c))

            d = {i: i for i in not_changed}
            d[c[-1]] = c[0]
            d.update({
                c[i]: c[i + 1] for i in range(len(c) - 1)
            })

            return group[
                Function(permutes, permutes, d)
            ]

        return type("SymmetricGroup", (Group,), {
            "name": "S{}".format(n),
            "_elements": set(all_permutation),
            "_identity": all_permutation[0],
            "operation": operation,
            "cycle": cycle,
        })()

    @classmethod
    def from_presentation(cls, els, relations):
        pass

    @property
    def identity(self):
        return GroupElement(self, self._identity)

    def inverse(self, a):
        for b in self:
            if self.operation(a, b) == self.identity:
                return b

    def operation(self, a, b):
        pass

    def compare(self, a, b):
        raise Exception("not implemented")

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


class Function:
    def __init__(self, domain, codomain, rule):
        # rule is a python function
        self.domain = domain
        self.codomain = codomain

        self.original_rule = rule

        if isinstance(rule, dict):
            self.rule = lambda g: rule[g]
        else:
            self.rule = rule

    def __hash__(self):
        return hash(tuple([self(i) for i in self.domain]))

    def is_homomorphism(self):
        for g1 in self.domain:
            for g2 in self.domain:
                if self(g1) * self(g2) != self(g1 * g2):
                    return False

        return True

    def kernel(self):
        return {el for el in self.domain if self(el) == self.codomain.identity}

    def injective(self):
        inverse_dict = {}

        for g in self.domain:
            inverse_dict[self(g)] = g
            for h in self.domain:
                if self(g) == self(h) and g != h:
                    return False

        self.left_inverse_dict = inverse_dict
        return True

    def surjective(self):
        inverse_dict = {}
        for g in self.domain:
            inverse_dict[self(g)] = g

        if len(inverse_dict) == len(self.codomain):
            self.right_inverse_dict = inverse_dict
            return True

        return False

    def bijective(self):
        return self.injective() and self.surjective()

    def __mul__(f, g):
        # composition.
        # we are f, other is g, we want f.g. domain of f must be codomain of g
        assert f.domain == g.codomain
        return Function(g.domain, f.codomain, lambda el: f.rule(g.rule(el)))

    def __call__(self, g):
        assert g in self.domain
        result = self.codomain[self.rule(g.token)]
        assert result in self.codomain

        return result

    def __str__(self):
        result = ["function {} => {}".format(self.domain, self.codomain)]
        for el in self.domain:
            result.append("    mapping {} -> {}".format(el.token, self(el).token))

        return "\n".join(result) + "\n\n"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if self.domain != other.domain or self.codomain != other.codomain:
            return False

        for el in self.domain:
            if self(el) != other(el):
                return False

        return True
