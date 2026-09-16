# Experimental engine patches / экспериментальные исправления

`krt-0.22.0-npth-via-floor.patch` targets [KiCadRoutingTools](https://github.com/drandyhaas/KiCadRoutingTools) commit `5a7fbcb6ee4deebd1d9ec1d5bd094d8681f502f3`. Its SHA256 is `f23c065706e02fd003d350f9cd4c308de7b5849981d98a023c10d43850884b03`. Upstream code is MIT-licensed; its notice is retained alongside this patch.

The patch consistently applies the declared copper-to-NPTH floor to via obstacles, post-route nudging and internal DRC. It includes seven regression tests, including the actual failing RF/UI coordinates. It does not weaken rules or change the Rust binary. Apply only to an isolated checkout with `git apply`; never mutate the pinned baseline while a comparison is running. Independent native KiCad validation remains mandatory. Passing unit tests alone is not routing or production acceptance.

Патч согласованно учитывает заданный зазор от меди до NPTH в препятствиях для via, последующем сдвиге via и внутреннем DRC. Семь тестов включают реальные ошибочные координаты RF/UI. Правила и Rust-бинарник не меняются. Применять через `git apply` только в отдельной копии указанной версии; исходный движок во время сравнения не менять. Независимая проверка KiCad обязательна; одних unit-тестов недостаточно для принятия трассировки или производства.
