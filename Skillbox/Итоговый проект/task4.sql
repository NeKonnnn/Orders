SELECT "TanderDemand"."ItemName"                                       AS "Product",
       "TanderDemand"."RequiredVolume"                                 AS "RequestedQuantity",
       CASE "TanderDemand"."DistributionCenter"
           WHEN 0 THEN 'РЦ Новосибирск Садовый (новый)'::text
           WHEN 1 THEN 'РЦ Кемерово'::text
           WHEN 2 THEN 'РЦ Омск'::text
           WHEN 3 THEN 'РЦ Тюмень'::text
           ELSE NULL::text
           END                                                         AS "DistributionCenter",
       "TanderDemand"."StartDeliveryDate"::timestamp without time zone AS "DeliveryStartDate",
       "TanderDemand"."EndDataTime"::timestamp without time zone       AS "AuctionEndDate",
       CASE "TanderDemand"."Status"
           WHEN 0 THEN 'Идут торги'::text
           WHEN 1 THEN 'Архив'::text
           ELSE NULL::text
           END                                                         AS "Status",
       "TanderDemand"."TargetPriceWithVat"                             AS "TargetPrice",
       "TanderDemand"."SupplierPriceWithVat"                           AS "BestPrice",
       'Тандер'::text                                                  AS "TradingPlatform"
FROM v2."TanderDemand"
UNION ALL
SELECT i."Title"                                          AS "Product",
       i."Quantity1"::numeric                             AS "RequestedQuantity",
       'РЦ Новоалтайск'::text                             AS "DistributionCenter",
       a."DeliveryStartDate"::timestamp without time zone AS "DeliveryStartDate",
       a."EndDateTime"::timestamp without time zone       AS "AuctionEndDate",
       CASE a."Status"
           WHEN 'Завершен'::text THEN 'Архив'::text
           ELSE 'Идут торги'::text
           END                                            AS "Status",
       i."StartBid"::numeric                              AS "TargetPrice",
       i."BestBid"::numeric                               AS "BestPrice",
       'МарияРа'::text                                    AS "TradingPlatform"
FROM v2."CislinkAuction" a
         JOIN v2."CislinkAuctionItem" i ON a."Id" = i."AuctionId"
UNION ALL
SELECT i."Title"                                          AS "Product",
       i."Quantity2"::numeric                             AS "RequestedQuantity",
       'РЦ Кемерово'::text                                AS "DistributionCenter",
       a."DeliveryStartDate"::timestamp without time zone AS "DeliveryStartDate",
       a."EndDateTime"::timestamp without time zone       AS "AuctionEndDate",
       CASE a."Status"
           WHEN 'Завершен'::text THEN 'Архив'::text
           ELSE 'Идут торги'::text
           END                                            AS "Status",
       i."StartBid"::numeric                              AS "TargetPrice",
       i."BestBid"::numeric                               AS "BestPrice",
       'МарияРа'::text                                    AS "TradingPlatform"
FROM v2."CislinkAuction" a
         JOIN v2."CislinkAuctionItem" i ON a."Id" = i."AuctionId";