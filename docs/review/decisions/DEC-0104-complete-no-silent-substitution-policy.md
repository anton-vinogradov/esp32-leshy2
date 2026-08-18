# DEC-0104 — complete no-silent-substitution policy

Статус: **принято автоматически; проведено ревью policy coverage**.

## Контекст

I8 requires every purchase line to have either a qualified exact alternate, a
bounded parametric policy or an explicit no-drop-in/requalification rule.
Simply naming the first MPN does not tell a factory which substitutions are
safe, while inventing 187 untested second sources would be worse.

The owner has delegated improvements and component maintenance that preserve
all functions without material cost growth. A conservative substitution
boundary changes no target function and therefore does not require a product
tradeoff decision.

## Решение

1. Every current purchase device id belongs to exactly one explicit class.
2. Eight classes separate RF/frequency, power passives, control/precision
   passives, discrete protection, logic/analog, power/safety ICs,
   compute/radio endpoints and mechanical/optical parts.
3. Each class defines both an equivalence envelope and mandatory
   requalification. A class is a disposition, not proof of a qualified second
   MPN.
4. Missing, duplicate, stale/non-purchase or malformed class membership fails
   generator validation.
5. The generated CSV exposes the class on every line; future factory RFQ may
   propose alternatives only inside that boundary.

## Consequences

- alternate/no-substitution policy coverage becomes `187/187`;
- no component, quantity, owner, pin, feature or diagram changes;
- no untested alternate becomes approved;
- at this decision's acceptance sourcing was `186/187` and cost was `0/187`;
  later `BOM-0013/DEC-0105/REV-0005BL` advances cost to 15/187 without changing
  this substitution policy;
- any proposed specific alternate still needs its class requalification before
  AVL acceptance.
