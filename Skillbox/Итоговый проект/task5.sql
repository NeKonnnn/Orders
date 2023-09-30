
























select distinct p."TransportPacking"
from public."ActiveProduct" p;



















-- Коробка
-- Carton = 1,
-- Ящик пластиковый
-- PlasticBox = 2,
-- Ящик деревянный
-- WoodenBox = 3,
-- Ящик алюминиевый
-- AluminumBox = 4,
-- Ящик пенопластовый
-- FoamBox = 5,
-- Мешок
-- Bag = 6,
-- Крафтмешок
-- CraftBag = 7,
-- Сетка-мешок
-- StringBag = 8,
-- Бочка
-- Barrel = 9,
-- Бидон
-- Can = 10,
-- Фляга
-- Flask = 11,
-- Цистерна
-- Tank = 12,
-- Ведро
-- Bucket = 13










select "Id", "Title" ->> 'ru-RU' as "Title", "Manufacturer", "TransportPacking"
from "ActiveProduct"
where "Title" ->> 'ru-RU' ilike '%ябл%';















select p."Id", p."Title" ->> 'ru-RU' as "Title", "Manufacturer", "TransportPacking", l."Price"
from "ActiveProduct" p
inner join public."PriceList" pl
on p."OwnerId" = pl."OwnerId" and pl."Status" = 0 and pl."IsDefault"
inner join public."PriceListLine" l
on pl."Id" = l."PriceListId" and p."Id" = l."EntityId"
where p."Title" ->> 'ru-RU' ilike '%ябл%';














select p."Id", p."Title" ->> 'ru-RU' as "Title", "Manufacturer", "TransportPacking", l."Price"
from "ActiveProduct" p
inner join public."PriceList" pl
on p."OwnerId" = pl."OwnerId" and pl."Status" = 0 and pl."IsDefault"
inner join public."PriceListLine" l
on pl."Id" = l."PriceListId" and p."Id" = l."EntityId"
where p."Title" ->> 'ru-RU' ilike '%ябл%'
    and p."TransportPacking" = 3
    --and l."Price" > 20
;








do $$

declare title_q text = '%ябл%';
declare minprice_q numeric;
declare maxprice_q numeric;
declare transportpacking_q json = '[7]';

declare transportpacking_count int := (select count(distinct(t #>> '{}')) from json_array_elements(transportpacking_q) t);

declare transportpacking_arr smallint[];
declare minprice numeric;
declare maxprice numeric;
declare query text;

begin

    drop table if exists public."AvailableFilters";

    create table public."AvailableFilters" as
    select distinct
           p."TransportPacking",
           min(l."Price") over() "MinPrice",
           max(l."Price") over() "MaxPrice"
    from public."ActiveProduct" p
    inner join public."PriceList" pl
    on p."OwnerId" = pl."OwnerId" and pl."Status" = 0 and pl."IsDefault"
    inner join public."PriceListLine" l
    on pl."Id" = l."PriceListId" and p."Id" = l."EntityId"
    where  (title_q is null or (title_q is not null and p."Title"->> 'ru-RU' ilike '%' || title_q || '%'))
           and (transportpacking_q is null or (transportpacking_q is not null and to_jsonb(transportpacking_q) @> to_jsonb(p."TransportPacking")))
           and (minprice_q is null or (minprice_q is not null and l."Price" >= minprice_q))
           and (maxprice_q is null or (maxprice_q is not null and l."Price" <= maxprice_q));

    if (transportpacking_count > 0)
    then
        transportpacking_arr := array(
                select distinct p."TransportPacking"
                from public."ActiveProduct" p
                inner join public."PriceList" pl
                       on p."OwnerId" = pl."OwnerId" and pl."Status" = 0 and pl."IsDefault"
                inner join public."PriceListLine" l
                       on pl."Id" = l."PriceListId" and p."Id" = l."EntityId"
                where (title_q is null or
                       (title_q is not null and p."Title" ->> 'ru-RU' ilike '%' || title_q || '%'))
                  and (minprice_q is null or (minprice_q is not null and l."Price" >= minprice_q))
                  and (maxprice_q is null or (maxprice_q is not null and l."Price" <= maxprice_q))
                  and p."TransportPacking" is not null
           );
    end if;

    if (minprice_q is not null)
    then
        minprice:= (
                select min(l."Price")
                from public."ActiveProduct" p
                inner join public."PriceList" pl
                       on p."OwnerId" = pl."OwnerId" and pl."Status" = 0 and pl."IsDefault"
                inner join public."PriceListLine" l
                       on pl."Id" = l."PriceListId" and p."Id" = l."EntityId"
                where (title_q is null or
                       (title_q is not null and p."Title" ->> 'ru-RU' ilike '%' || title_q || '%'))
                  and (transportpacking_q is null or (transportpacking_q is not null and
                                                      to_jsonb(transportpacking_q) @> to_jsonb(p."TransportPacking")))
                  and (maxprice_q is null or (maxprice_q is not null and l."Price" <= maxprice_q))
                  and l."Price" is not null
                       );
    end if;

    if (maxprice_q is not null)
    then
        maxprice:= (
                select max(l."Price")
                from public."ActiveProduct" p
                inner join public."PriceList" pl
                       on p."OwnerId" = pl."OwnerId" and pl."Status" = 0 and pl."IsDefault"
                inner join public."PriceListLine" l
                       on pl."Id" = l."PriceListId" and p."Id" = l."EntityId"
                inner join public."Category" c3
                    on p."CategoryId3" = c3."Id" and c3."Level" = 3
                where (title_q is null or
                       (title_q is not null and p."Title" ->> 'ru-RU' ilike '%' || title_q || '%'))
                  and (transportpacking_q is null or (transportpacking_q is not null and
                                                      to_jsonb(transportpacking_q) @> to_jsonb(p."TransportPacking")))
                  and (minprice_q is null or (minprice_q is not null and l."Price" >= minprice_q))
                  and l."Price" is not null
                       );
    end if;

    query := $code$
    select $code$;

    if (transportpacking_count > 0)
    then
        query := query || $code$TransportPacking_t::smallint, $code$;
    else
        query := query || $code$null::smallint TransportPacking_t, $code$;
    end if;

    query := query || coalesce(minprice::text || '::numeric minprice', 'null::numeric minprice') || ', ' || coalesce(maxprice::text || '::numeric maxprice', 'null::numeric maxprice') || $code$
    from $code$;

    if (transportpacking_count > 0)
    then
        query := query || $code$unnest(array[$code$ || array_to_string(transportpacking_arr, ',', '') || $code$]) TransportPacking_t$code$;
    else
        query := query || $code$(select null) TransportPacking_t$code$;
    end if;

    raise notice '%', query;

end $$;

select * from public."AvailableFilters";


















-- Строка обратного индекса для фильтров по продуктам
-- FilterReverseIndex
-- {
--     Идентификатор верхней категории
--     Guid CategoryId1
--
--     Идентификатор средней категории
--     Guid CategoryId2
--
--     Идентификатор нижней категории
--     Guid CategoryId3
--
--     Идентификатор поставщика
--     Guid OwnerId
--
--     Страна происхождения
--     Country CountryOfOrigin
--
--     Минимальная цена
--     decimal MinPrice
--
--     Максимальная цена
--     decimal MaxPrice
-- }