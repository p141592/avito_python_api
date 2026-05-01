# Swagger Contract Backlog

Дата фиксации: 2026-05-01.

Команды baseline:

```bash
poetry run pytest tests/contracts/test_swagger_contracts.py -k request_body_matches --tb=short
poetry run pytest tests/contracts/test_swagger_contracts.py -k "success_response_models_accept or error_responses_preserve" --tb=short
```

Результат:

- request body schema: 85 failed, 119 passed, 1707 deselected;
- success/error schema: 61 failed, 782 passed, 1068 deselected.

## Request Body Mismatches

### accounts - 1

- `ИерархияАккаунтов.json POST /listItemsByEmployeeIdV1`

### ads - 7

- `Объявления.json PUT /core/v1/accounts/{user_id}/items/{item_id}/vas`
- `Объявления.json PUT /core/v2/items/{item_id}/vas`
- `Объявления.json PUT /core/v2/accounts/{user_id}/items/{item_id}/vas_packages`
- `Объявления.json POST /stats/v2/accounts/{user_id}/spendings`
- `Объявления.json POST /core/v1/accounts/{user_id}/calls/stats`
- `Объявления.json POST /stats/v2/accounts/{user_id}/items`
- `Объявления.json POST /stats/v1/accounts/{user_id}/items`

### autoload - 2

- `Автозагрузка.json POST /autoload/v1/profile`
- `Автозагрузка.json POST /autoload/v2/profile`

### autoteka - 10

- `Автотека.json POST /autoteka/v1/monitoring/bucket/add`
- `Автотека.json POST /autoteka/v1/monitoring/bucket/remove`
- `Автотека.json POST /autoteka/v1/reports-by-vehicle-id`
- `Автотека.json POST /autoteka/v1/scoring/by-vehicle-id`
- `Автотека.json POST /autoteka/v1/valuation/by-specification`
- `Автотека.json POST /autoteka/v1/request-preview-by-external-item`
- `Автотека.json POST /autoteka/v1/specifications/by-vehicle-id`
- `Автотека.json POST /autoteka/v1/teasers`
- `Автотека.json POST /autoteka/v1/get-leads`
- `Автотека.json POST /autoteka/v1/catalogs/resolve`

### cpa - 8

- `CPAАвито.json POST /cpa/v2/balanceInfo`
- `CPAАвито.json POST /cpa/v1/createComplaint`
- `CPAАвито.json POST /cpa/v2/callsByTime`
- `CPAАвито.json POST /cpa/v1/phonesInfoFromChats`
- `CPAАвито.json POST /cpa/v2/chatsByTime`
- `CPAАвито.json POST /cpa/v1/chatsByTime`
- `CPAАвито.json POST /cpa/v1/createComplaintByActionId`
- `CPAАвито.json POST /cpa/v3/balanceInfo`

### jobs - 8

- `АвитоРабота.json POST /job/v1/applications/apply_actions`
- `АвитоРабота.json POST /job/v1/applications/get_by_ids`
- `АвитоРабота.json PUT /job/v1/applications/webhook`
- `АвитоРабота.json POST /job/v2/vacancies`
- `АвитоРабота.json POST /job/v1/vacancies`
- `АвитоРабота.json POST /job/v2/vacancies/statuses`
- `АвитоРабота.json POST /job/v2/vacancies/update/{vacancy_uuid}`
- `АвитоРабота.json PUT /job/v1/vacancies/{vacancy_id}`

### messenger - 3

- `Мессенджер.json POST /messenger/v2/accounts/{user_id}/blacklist`
- `Мессенджер.json POST /messenger/v1/accounts/{user_id}/chats/{chat_id}/messages/image`
- `Мессенджер.json POST /messenger/v1/accounts/{user_id}/chats/{chat_id}/messages`

### special-offers - 3

- `Рассылкаскидокиспецпредложенийвмессенджере.json POST /special-offers/v1/multiConfirm`
- `Рассылкаскидокиспецпредложенийвмессенджере.json POST /special-offers/v1/multiCreate`
- `Рассылкаскидокиспецпредложенийвмессенджере.json POST /special-offers/v1/stats`

### delivery - 5

- `Доставка.json POST /createParcel`
- `Доставка.json POST /createAnnouncement`
- `Доставка.json POST /delivery/order/changeParcelResult`
- `Доставка.json POST /cancelAnnouncement`
- `Доставка.json POST /sandbox/changeParcels`

### orders - 9

- `Управлениезаказами.json POST /order-management/1/order/acceptReturnOrder`
- `Управлениезаказами.json POST /order-management/1/order/applyTransition`
- `Управлениезаказами.json POST /order-management/1/order/checkConfirmationCode`
- `Управлениезаказами.json POST /order-management/1/order/cncSetDetails`
- `Управлениезаказами.json POST /order-management/1/order/setCourierDeliveryRange`
- `Управлениезаказами.json POST /order-management/1/markings`
- `Управлениезаказами.json POST /order-management/1/order/setTrackingNumber`
- `Управлениезаказами.json POST /order-management/1/orders/labels`
- `Управлениезаказами.json POST /order-management/1/orders/labels/extended`

### delivery sandbox - 18

- `Доставка.json POST /delivery-sandbox/tariffs/{tariff_id}/areas`
- `Доставка.json POST /delivery-sandbox/tariffs/sorting-center`
- `Доставка.json POST /delivery-sandbox/tariffs/{tariff_id}/tagged-sorting-centers`
- `Доставка.json POST /delivery-sandbox/tariffsV2`
- `Доставка.json POST /delivery-sandbox/tariffs/{tariff_id}/terminals`
- `Доставка.json POST /delivery-sandbox/cancelParcel`
- `Доставка.json POST /delivery-sandbox/v1/cancelParcel`
- `Доставка.json POST /delivery-sandbox/v1/changeParcel`
- `Доставка.json POST /delivery-sandbox/order/checkConfirmationCode`
- `Доставка.json POST /delivery-sandbox/announcements/create`
- `Доставка.json POST /delivery-sandbox/v2/createParcel`
- `Доставка.json POST /delivery-sandbox/v1/getParcelInfo`
- `Доставка.json POST /delivery-sandbox/v1/getRegisteredParcelID`
- `Доставка.json POST /delivery-sandbox/prohibitOrderAcceptance`
- `Доставка.json POST /delivery-sandbox/order/properties`
- `Доставка.json POST /delivery-sandbox/order/realAddress`
- `Доставка.json POST /delivery-sandbox/announcements/track`
- `Доставка.json POST /delivery-sandbox/order/tracking`

### stock - 1

- `Управлениеостатками.json POST /stock-management/1/info`

### autostrategy - 2

- `Автостратегия.json POST /autostrategy/v1/campaign/stop`
- `Автостратегия.json POST /autostrategy/v1/campaign/edit`

### promotion - 2

- `Продвижение.json POST /promotion/v1/items/services/orders/status`
- `Продвижение.json POST /promotion/v1/items/services/orders/get`

### trx-promo - 1

- `TrxPromo.json POST /trx-promo/1/cancel`

### ratings - 1

- `Рейтингииотзывы.json POST /ratings/v1/answers`

### realty - 4

- `Краткосрочнаяаренда.json POST /core/v1/accounts/{user_id}/items/{item_id}/bookings`
- `Краткосрочнаяаренда.json POST /realty/v1/items/intervals`
- `Краткосрочнаяаренда.json POST /realty/v1/items/{item_id}/base`
- `Краткосрочнаяаренда.json POST /realty/v1/accounts/{user_id}/items/{item_id}/prices`

## Success Response Mismatches

### accounts - 3

- `Информацияопользователе.json POST /core/v1/accounts/operations_history`
- `ИерархияАккаунтов.json GET /listCompanyPhonesV1`
- `ИерархияАккаунтов.json GET /getEmployeesV1`

### ads - 1

- `Объявления.json POST /core/v1/accounts/{user_id}/vas/prices`

### autoload - 3

- `Автозагрузка.json GET /autoload/v3/reports/{report_id}`
- `Автозагрузка.json GET /autoload/v2/reports/{report_id}/items/fees`
- `Автозагрузка.json GET /autoload/v3/reports/last_completed_report`

### jobs - 1

- `АвитоРабота.json POST /job/v2/vacancies/statuses`

### messenger - 1

- `Мессенджер.json GET /messenger/v3/accounts/{user_id}/chats/{chat_id}/messages`

### delivery - 1

- `Доставка.json GET /delivery-sandbox/sorting-center`

### promotion - 1

- `Продвижение.json POST /promotion/v1/items/services/dict`

### auth/autoteka token - 4

- `Авторизация.json POST /token‎`
- `Авторизация.json POST /token‎‎`
- `Автотека.json POST /token`
- `Авторизация.json POST /token`

## Error Response Mismatches

### autostrategy 500 errors - 7

- `Автостратегия.json POST /autostrategy/v1/budget 500`
- `Автостратегия.json POST /autostrategy/v1/campaign/create 500`
- `Автостратегия.json POST /autostrategy/v1/campaign/edit 500`
- `Автостратегия.json POST /autostrategy/v1/campaign/info 500`
- `Автостратегия.json POST /autostrategy/v1/campaign/stop 500`
- `Автостратегия.json POST /autostrategy/v1/campaigns 500`
- `Автостратегия.json POST /autostrategy/v1/stat 500`

### delivery errors - 39

- `Доставка.json POST /cancelAnnouncement 401`
- `Доставка.json POST /cancelAnnouncement 403`
- `Доставка.json POST /createAnnouncement 401`
- `Доставка.json POST /createAnnouncement 403`
- `Доставка.json POST /createParcel 401`
- `Доставка.json POST /createParcel 403`
- `Доставка.json POST /delivery-sandbox/announcements/create 401`
- `Доставка.json POST /delivery-sandbox/announcements/create 403`
- `Доставка.json POST /delivery-sandbox/announcements/track 401`
- `Доставка.json POST /delivery-sandbox/announcements/track 403`
- `Доставка.json POST /delivery-sandbox/areas/custom-schedule 401`
- `Доставка.json POST /delivery-sandbox/cancelParcel 401`
- `Доставка.json POST /delivery-sandbox/order/checkConfirmationCode 401`
- `Доставка.json POST /delivery-sandbox/order/checkConfirmationCode 403`
- `Доставка.json POST /delivery-sandbox/order/properties 401`
- `Доставка.json POST /delivery-sandbox/order/properties 403`
- `Доставка.json POST /delivery-sandbox/order/realAddress 401`
- `Доставка.json POST /delivery-sandbox/order/realAddress 403`
- `Доставка.json POST /delivery-sandbox/order/tracking 401`
- `Доставка.json POST /delivery-sandbox/order/tracking 403`
- `Доставка.json POST /delivery-sandbox/prohibitOrderAcceptance 401`
- `Доставка.json GET /delivery-sandbox/sorting-center 401`
- `Доставка.json GET /delivery-sandbox/sorting-center 403`
- `Доставка.json POST /delivery-sandbox/tariffs/sorting-center 401`
- `Доставка.json POST /delivery-sandbox/tariffs/sorting-center 403`
- `Доставка.json POST /delivery-sandbox/tariffs/{tariff_id}/areas 401`
- `Доставка.json POST /delivery-sandbox/tariffs/{tariff_id}/areas 403`
- `Доставка.json POST /delivery-sandbox/tariffs/{tariff_id}/tagged-sorting-centers 401`
- `Доставка.json POST /delivery-sandbox/tariffs/{tariff_id}/tagged-sorting-centers 403`
- `Доставка.json POST /delivery-sandbox/tariffs/{tariff_id}/terminals 401`
- `Доставка.json POST /delivery-sandbox/tariffs/{tariff_id}/terminals 403`
- `Доставка.json POST /delivery-sandbox/tariffs/{tariff_id}/terms 401`
- `Доставка.json POST /delivery-sandbox/tariffs/{tariff_id}/terms 403`
- `Доставка.json POST /delivery-sandbox/tariffsV2 401`
- `Доставка.json POST /delivery-sandbox/tariffsV2 403`
- `Доставка.json GET /delivery-sandbox/tasks/{task_id} 401`
- `Доставка.json GET /delivery-sandbox/tasks/{task_id} 403`
- `Доставка.json POST /sandbox/changeParcels 401`
- `Доставка.json POST /sandbox/changeParcels 403`
