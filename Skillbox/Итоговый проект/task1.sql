select *
from a."AuditEntry";

select *
from a."AuditEntryProperty" ap;














select distinct "State", "StateName"
from a."AuditEntry";

select distinct "EntityTypeName"
from a."AuditEntry";







select *
from a."AuditEntry" a
where a."State" = 0;







select *
from a."AuditEntryProperty" ap
where ap."AuditEntryID" = 1;







select
    ap1."NewValue" as "Email",
    ap2."NewValue" as "PhoneNumber"
from a."AuditEntryProperty" ap1
inner join a."AuditEntryProperty" ap2
    on ap1."AuditEntryID" = ap2."AuditEntryID"
where ap1."PropertyName" = 'Email'
and ap2."PropertyName" = 'PhoneNumber'
and ap1."AuditEntryID" = 1;





select
    ap1."NewValue" as "Id",
    ap2."NewValue" as "ChangedById",
    ap3."NewValue" as "ChangedDate",
    ap4."NewValue" as "ChangedOnBehalfId",
    ap5."NewValue" as "CreatedById",
    ap6."NewValue" as "CreatedDate",
    ap7."NewValue" as "CreatedOnBehalfId",
    ap8."NewValue" as "DeletedById",
    ap9."NewValue" as "DeletedDate",
    ap10."NewValue" as "DeletedOnBehalfId",
    ap11."NewValue" as "Email",
    ap12."NewValue" as "FirstName",
    ap13."NewValue" as "IconUrl",
    ap14."NewValue" as "IsOperator",
    ap15."NewValue" as "IsTestUser",
    ap16."NewValue" as "LastName",
    ap17."NewValue" as "MiddleName",
    ap18."NewValue" as "PasswordHash",
    ap19."NewValue" as "PhoneNumber",
    ap20."NewValue" as "SoftDeletedLevel",
    ap21."NewValue" as "UserName"
from a."AuditEntryProperty" ap1
inner join a."AuditEntryProperty" ap2
    on ap1."AuditEntryID" = ap2."AuditEntryID"
inner join a."AuditEntryProperty" ap3
    on ap1."AuditEntryID" = ap3."AuditEntryID"
inner join a."AuditEntryProperty" ap4
    on ap1."AuditEntryID" = ap4."AuditEntryID"
inner join a."AuditEntryProperty" ap5
    on ap1."AuditEntryID" = ap5."AuditEntryID"
inner join a."AuditEntryProperty" ap6
    on ap1."AuditEntryID" = ap6."AuditEntryID"
inner join a."AuditEntryProperty" ap7
    on ap1."AuditEntryID" = ap7."AuditEntryID"
inner join a."AuditEntryProperty" ap8
    on ap1."AuditEntryID" = ap8."AuditEntryID"
inner join a."AuditEntryProperty" ap9
    on ap1."AuditEntryID" = ap9."AuditEntryID"
inner join a."AuditEntryProperty" ap10
    on ap1."AuditEntryID" = ap10."AuditEntryID"
inner join a."AuditEntryProperty" ap11
    on ap1."AuditEntryID" = ap11."AuditEntryID"
inner join a."AuditEntryProperty" ap12
    on ap1."AuditEntryID" = ap12."AuditEntryID"
inner join a."AuditEntryProperty" ap13
    on ap1."AuditEntryID" = ap13."AuditEntryID"
inner join a."AuditEntryProperty" ap14
    on ap1."AuditEntryID" = ap14."AuditEntryID"
inner join a."AuditEntryProperty" ap15
    on ap1."AuditEntryID" = ap15."AuditEntryID"
inner join a."AuditEntryProperty" ap16
    on ap1."AuditEntryID" = ap16."AuditEntryID"
inner join a."AuditEntryProperty" ap17
    on ap1."AuditEntryID" = ap17."AuditEntryID"
inner join a."AuditEntryProperty" ap18
    on ap1."AuditEntryID" = ap18."AuditEntryID"
inner join a."AuditEntryProperty" ap19
    on ap1."AuditEntryID" = ap19."AuditEntryID"
inner join a."AuditEntryProperty" ap20
    on ap1."AuditEntryID" = ap20."AuditEntryID"
inner join a."AuditEntryProperty" ap21
    on ap1."AuditEntryID" = ap21."AuditEntryID"
where ap1."PropertyName" = 'Id'
and ap2."PropertyName" = 'ChangedById'
and ap3."PropertyName" = 'ChangedDate'
and ap4."PropertyName" = 'ChangedOnBehalfId'
and ap5."PropertyName" = 'CreatedById'
and ap6."PropertyName" = 'CreatedDate'
and ap7."PropertyName" = 'CreatedOnBehalfId'
and ap8."PropertyName" = 'DeletedById'
and ap9."PropertyName" = 'DeletedDate'
and ap10."PropertyName" = 'DeletedOnBehalfId'
and ap11."PropertyName" = 'Email'
and ap12."PropertyName" = 'FirstName'
and ap13."PropertyName" = 'IconUrl'
and ap14."PropertyName" = 'IsOperator'
and ap15."PropertyName" = 'IsTestUser'
and ap16."PropertyName" = 'LastName'
and ap17."PropertyName" = 'MiddleName'
and ap18."PropertyName" = 'PasswordHash'
and ap19."PropertyName" = 'PhoneNumber'
and ap20."PropertyName" = 'SoftDeletedLevel'
and ap21."PropertyName" = 'UserName'
and ap1."AuditEntryID" = 1;











select *
from a."AuditEntry"
where "AuditEntryID" = 1;











select a.*
from a."AuditEntry" a
inner join a."AuditEntryProperty" ap
    on a."AuditEntryID" =  ap."AuditEntryID"
    and ap."PropertyName" = 'Id'
    and (ap."OldValue" = '0a584f01-22f0-4d38-8601-ef0b3ea060dd'
    or ap."NewValue" = '0a584f01-22f0-4d38-8601-ef0b3ea060dd');







select *
from a."AuditEntry" a
where a."StateName" = 'EntityModified'
and a."EntityTypeName" = 'User';










select *
from a."AuditEntryProperty"
where "AuditEntryID" = 5;














select a.*
from a."AuditEntry" a
inner join a."AuditEntryProperty" ap
    on a."AuditEntryID" =  ap."AuditEntryID"
    and ap."PropertyName" = 'Id'
    and (ap."OldValue" = '9e53508d-c319-4259-bbcb-72016eae0881'
    or ap."NewValue" = '9e53508d-c319-4259-bbcb-72016eae0881');









select *
from v2."User"
where "Id" = '9e53508d-c319-4259-bbcb-72016eae0881';






select max(a."AuditEntryID") as "AuditEntryID" --последнее примененное изменение
from a."AuditEntry" a
inner join a."AuditEntryProperty" ap
    on a."AuditEntryID" =  ap."AuditEntryID"
    and ap."PropertyName" = 'Id'
    and (ap."OldValue" = '9e53508d-c319-4259-bbcb-72016eae0881'
    or ap."NewValue" = '9e53508d-c319-4259-bbcb-72016eae0881')
where "CreatedDate" <= '2022-10-25';










select a."AuditEntryID" as "AddedId"
from a."AuditEntry" a
inner join a."AuditEntryProperty" ap
    on a."AuditEntryID" =  ap."AuditEntryID"
    and ap."PropertyName" = 'Id'
    and (ap."OldValue" = '9e53508d-c319-4259-bbcb-72016eae0881'
    or ap."NewValue" = '9e53508d-c319-4259-bbcb-72016eae0881')
where a."StateName" = 'EntityAdded'
limit 1;






select a."AuditEntryID" as "AddedId"
from a."AuditEntry" a
inner join a."AuditEntryProperty" ap
    on a."AuditEntryID" =  ap."AuditEntryID"
    and ap."PropertyName" = 'Id'
    and (ap."OldValue" = '0a584f01-22f0-4d38-8601-ef0b3ea060dd'
    or ap."NewValue" = '0a584f01-22f0-4d38-8601-ef0b3ea060dd')
where a."StateName" = 'EntityAdded'
limit 1;











select a."AuditEntryID" as "DeletedId"
from a."AuditEntry" a
inner join a."AuditEntryProperty" ap
    on a."AuditEntryID" =  ap."AuditEntryID"
    and ap."PropertyName" = 'Id'
    and (ap."OldValue" = '0a584f01-22f0-4d38-8601-ef0b3ea060dd'
    or ap."NewValue" = '0a584f01-22f0-4d38-8601-ef0b3ea060dd')
where a."StateName" = 'EntityDeleted'
limit 1;







select a1."AuditEntryID" as "AddedId",
       a2."AuditEntryID" as "ModifiedId",
       a1."CreatedDate" as "AddedDate",
       a2."CreatedDate" as "Modifieddate",
       coalesce(ap1."OldValue", ap1."NewValue", ap2."OldValue", ap2."NewValue") as "UserId"
from a."AuditEntry" a1
inner join a."AuditEntryProperty" ap1
    on a1."AuditEntryID" =  ap1."AuditEntryID"
    and ap1."PropertyName" = 'Id'
inner join a."AuditEntryProperty" ap2
    on ap2."PropertyName" = 'Id'
    and (ap2."OldValue" = ap1."OldValue" or ap2."NewValue" = ap1."OldValue"
    or ap2."NewValue" = ap1."OldValue" or ap2."NewValue" = ap1."NewValue")
inner join a."AuditEntry" a2
    on a2."AuditEntryID" =  ap2."AuditEntryID"
where a1."StateName" = 'EntityAdded' and a2."StateName" = 'EntityModified';











select a.*
from a."AuditEntry" a
inner join a."AuditEntryProperty" ap
    on a."AuditEntryID" =  ap."AuditEntryID"
    and ap."PropertyName" = 'Id'
    and (ap."OldValue" = '31d6bca7-ed7c-4f27-9627-7a68fbb7db77'
    or ap."NewValue" = '31d6bca7-ed7c-4f27-9627-7a68fbb7db77');








with last_updated_id("LastUpdatedId") as
    (
        select max(a."AuditEntryID") as "LastUpdatedId" --последнее примененное изменение
        from a."AuditEntry" a
        inner join a."AuditEntryProperty" ap
            on a."AuditEntryID" =  ap."AuditEntryID"
            and ap."PropertyName" = 'Id'
            and (ap."OldValue" = '31d6bca7-ed7c-4f27-9627-7a68fbb7db77'
            or ap."NewValue" = '31d6bca7-ed7c-4f27-9627-7a68fbb7db77')
        where "CreatedDate" <= '2023-01-01'
    ),
    added_id("AddedId") as
    (
        select a."AuditEntryID" as "AddedId" --операция создания
        from a."AuditEntry" a
        inner join a."AuditEntryProperty" ap
            on a."AuditEntryID" =  ap."AuditEntryID"
            and ap."PropertyName" = 'Id'
            and (ap."OldValue" = '31d6bca7-ed7c-4f27-9627-7a68fbb7db77'
            or ap."NewValue" = '31d6bca7-ed7c-4f27-9627-7a68fbb7db77')
        where a."StateName" = 'EntityAdded'
        limit 1
    ),
    initial_value("Id", "ChangedById", "ChangedDate", "ChangedOnBehalfId", "CreatedById", "CreatedDate", "CreatedOnBehalfId",
                "DeletedById", "DeletedDate", "DeletedOnBehalfId", "Email", "FirstName", "IconUrl", "IsOperator",
                "IsTestUser", "LastName", "MiddleName", "PasswordHash", "PhoneNumber", "SoftDeletedLevel", "UserName")
    as
    (
         select
            ap1."NewValue" as "Id",
            ap2."NewValue" as "ChangedById",
            ap3."NewValue" as "ChangedDate",
            ap4."NewValue" as "ChangedOnBehalfId",
            ap5."NewValue" as "CreatedById",
            ap6."NewValue" as "CreatedDate",
            ap7."NewValue" as "CreatedOnBehalfId",
            ap8."NewValue" as "DeletedById",
            ap9."NewValue" as "DeletedDate",
            ap10."NewValue" as "DeletedOnBehalfId",
            ap11."NewValue" as "Email",
            ap12."NewValue" as "FirstName",
            ap13."NewValue" as "IconUrl",
            ap14."NewValue" as "IsOperator",
            ap15."NewValue" as "IsTestUser",
            ap16."NewValue" as "LastName",
            ap17."NewValue" as "MiddleName",
            ap18."NewValue" as "PasswordHash",
            ap19."NewValue" as "PhoneNumber",
            ap20."NewValue" as "SoftDeletedLevel",
            ap21."NewValue" as "UserName"
        from a."AuditEntryProperty" ap1
        inner join a."AuditEntryProperty" ap2
            on ap1."AuditEntryID" = ap2."AuditEntryID"
        inner join a."AuditEntryProperty" ap3
            on ap1."AuditEntryID" = ap3."AuditEntryID"
        inner join a."AuditEntryProperty" ap4
            on ap1."AuditEntryID" = ap4."AuditEntryID"
        inner join a."AuditEntryProperty" ap5
            on ap1."AuditEntryID" = ap5."AuditEntryID"
        inner join a."AuditEntryProperty" ap6
            on ap1."AuditEntryID" = ap6."AuditEntryID"
        inner join a."AuditEntryProperty" ap7
            on ap1."AuditEntryID" = ap7."AuditEntryID"
        inner join a."AuditEntryProperty" ap8
            on ap1."AuditEntryID" = ap8."AuditEntryID"
        inner join a."AuditEntryProperty" ap9
            on ap1."AuditEntryID" = ap9."AuditEntryID"
        inner join a."AuditEntryProperty" ap10
            on ap1."AuditEntryID" = ap10."AuditEntryID"
        inner join a."AuditEntryProperty" ap11
            on ap1."AuditEntryID" = ap11."AuditEntryID"
        inner join a."AuditEntryProperty" ap12
            on ap1."AuditEntryID" = ap12."AuditEntryID"
        inner join a."AuditEntryProperty" ap13
            on ap1."AuditEntryID" = ap13."AuditEntryID"
        inner join a."AuditEntryProperty" ap14
            on ap1."AuditEntryID" = ap14."AuditEntryID"
        inner join a."AuditEntryProperty" ap15
            on ap1."AuditEntryID" = ap15."AuditEntryID"
        inner join a."AuditEntryProperty" ap16
            on ap1."AuditEntryID" = ap16."AuditEntryID"
        inner join a."AuditEntryProperty" ap17
            on ap1."AuditEntryID" = ap17."AuditEntryID"
        inner join a."AuditEntryProperty" ap18
            on ap1."AuditEntryID" = ap18."AuditEntryID"
        inner join a."AuditEntryProperty" ap19
            on ap1."AuditEntryID" = ap19."AuditEntryID"
        inner join a."AuditEntryProperty" ap20
            on ap1."AuditEntryID" = ap20."AuditEntryID"
        inner join a."AuditEntryProperty" ap21
            on ap1."AuditEntryID" = ap21."AuditEntryID"
        inner join added_id
            on ap1."AuditEntryID" = added_id."AddedId"
        where ap1."PropertyName" = 'Id'
        and ap2."PropertyName" = 'ChangedById'
        and ap3."PropertyName" = 'ChangedDate'
        and ap4."PropertyName" = 'ChangedOnBehalfId'
        and ap5."PropertyName" = 'CreatedById'
        and ap6."PropertyName" = 'CreatedDate'
        and ap7."PropertyName" = 'CreatedOnBehalfId'
        and ap8."PropertyName" = 'DeletedById'
        and ap9."PropertyName" = 'DeletedDate'
        and ap10."PropertyName" = 'DeletedOnBehalfId'
        and ap11."PropertyName" = 'Email'
        and ap12."PropertyName" = 'FirstName'
        and ap13."PropertyName" = 'IconUrl'
        and ap14."PropertyName" = 'IsOperator'
        and ap15."PropertyName" = 'IsTestUser'
        and ap16."PropertyName" = 'LastName'
        and ap17."PropertyName" = 'MiddleName'
        and ap18."PropertyName" = 'PasswordHash'
        and ap19."PropertyName" = 'PhoneNumber'
        and ap20."PropertyName" = 'SoftDeletedLevel'
        and ap21."PropertyName" = 'UserName'
    ),
    operations("OperationId") as
        (
            select a."AuditEntryID" "OperartionId"
            from added_id
            inner join a."AuditEntry" a
                on "AddedId" <= a."AuditEntryID"
            inner join last_updated_id
                on a."AuditEntryID" <= "LastUpdatedId"
            inner join a."AuditEntryProperty" ap
                on a."AuditEntryID" =  ap."AuditEntryID"
                and ap."PropertyName" = 'Id'
                and (ap."OldValue" = '31d6bca7-ed7c-4f27-9627-7a68fbb7db77'
                or ap."NewValue" = '31d6bca7-ed7c-4f27-9627-7a68fbb7db77')
        ),
    current_value("Id", "ChangedById", "ChangedDate", "ChangedOnBehalfId", "CreatedById", "CreatedDate", "CreatedOnBehalfId",
                "DeletedById", "DeletedDate", "DeletedOnBehalfId", "Email", "FirstName", "IconUrl", "IsOperator",
                "IsTestUser", "LastName", "MiddleName", "PasswordHash", "PhoneNumber", "SoftDeletedLevel", "UserName")
        as
    (
        select
            (select ap."NewValue"
             from a."AuditEntryProperty" ap
             inner join operations
                on ap."AuditEntryID" = "OperationId"
             where ap."PropertyName" = 'Id'
             order by ap."AuditEntryID" desc
             limit 1) as "Id",
            (select ap."NewValue"
             from a."AuditEntryProperty" ap
             inner join operations
                on ap."AuditEntryID" = "OperationId"
             where ap."PropertyName" = 'ChangedById'
             order by ap."AuditEntryID" desc
             limit 1) as "ChangedById",
            (select ap."NewValue"
             from a."AuditEntryProperty" ap
             inner join operations
                on ap."AuditEntryID" = "OperationId"
             where ap."PropertyName" = 'ChangedDate'
             order by ap."AuditEntryID" desc
             limit 1) as "ChangedDate",
            (select ap."NewValue"
             from a."AuditEntryProperty" ap
             inner join operations
                on ap."AuditEntryID" = "OperationId"
             where ap."PropertyName" = 'ChangedOnBehalfId'
             order by ap."AuditEntryID" desc
             limit 1) as "ChangedOnBehalfId",
            (select ap."NewValue"
             from a."AuditEntryProperty" ap
             inner join operations
                on ap."AuditEntryID" = "OperationId"
             where ap."PropertyName" = 'CreatedById'
             order by ap."AuditEntryID" desc
             limit 1) as "CreatedById",
            (select ap."NewValue"
             from a."AuditEntryProperty" ap
             inner join operations
                on ap."AuditEntryID" = "OperationId"
             where ap."PropertyName" = 'CreatedDate'
             order by ap."AuditEntryID" desc
             limit 1) as "CreatedDate",
            (select ap."NewValue"
             from a."AuditEntryProperty" ap
             inner join operations
                on ap."AuditEntryID" = "OperationId"
             where ap."PropertyName" = 'CreatedOnBehalfId'
             order by ap."AuditEntryID" desc
             limit 1) as "CreatedOnBehalfId",
            (select ap."NewValue"
             from a."AuditEntryProperty" ap
             inner join operations
                on ap."AuditEntryID" = "OperationId"
             where ap."PropertyName" = 'DeletedById'
             order by ap."AuditEntryID" desc
             limit 1) as "DeletedById",
            (select ap."NewValue"
             from a."AuditEntryProperty" ap
             inner join operations
                on ap."AuditEntryID" = "OperationId"
             where ap."PropertyName" = 'DeletedDate'
             order by ap."AuditEntryID" desc
             limit 1) as "DeletedDate",
            (select ap."NewValue"
             from a."AuditEntryProperty" ap
             inner join operations
                on ap."AuditEntryID" = "OperationId"
             where ap."PropertyName" = 'DeletedOnBehalfId'
             order by ap."AuditEntryID" desc
             limit 1) as "DeletedOnBehalfId",
            (select ap."NewValue"
             from a."AuditEntryProperty" ap
             inner join operations
                on ap."AuditEntryID" = "OperationId"
             where ap."PropertyName" = 'Email'
             order by ap."AuditEntryID" desc
             limit 1) as "Email",
            (select ap."NewValue"
             from a."AuditEntryProperty" ap
             inner join operations
                on ap."AuditEntryID" = "OperationId"
             where ap."PropertyName" = 'FirstName'
             order by ap."AuditEntryID" desc
             limit 1) as "FirstName",
            (select ap."NewValue"
             from a."AuditEntryProperty" ap
             inner join operations
                on ap."AuditEntryID" = "OperationId"
             where ap."PropertyName" = 'IconUrl'
             order by ap."AuditEntryID" desc
             limit 1) as "IconUrl",
            (select ap."NewValue"
             from a."AuditEntryProperty" ap
             inner join operations
                on ap."AuditEntryID" = "OperationId"
             where ap."PropertyName" = 'IsOperator'
             order by ap."AuditEntryID" desc
             limit 1) as "IsOperator",
            (select ap."NewValue"
             from a."AuditEntryProperty" ap
             inner join operations
                on ap."AuditEntryID" = "OperationId"
             where ap."PropertyName" = 'IsTestUser'
             order by ap."AuditEntryID" desc
             limit 1) as "IsTestUser",
            (select ap."NewValue"
             from a."AuditEntryProperty" ap
             inner join operations
                on ap."AuditEntryID" = "OperationId"
             where ap."PropertyName" = 'LastName'
             order by ap."AuditEntryID" desc
             limit 1) as "LastName",
            (select ap."NewValue"
             from a."AuditEntryProperty" ap
             inner join operations
                on ap."AuditEntryID" = "OperationId"
             where ap."PropertyName" = 'MiddleName'
             order by ap."AuditEntryID" desc
             limit 1) as "MiddleName",
            (select ap."NewValue"
             from a."AuditEntryProperty" ap
             inner join operations
                on ap."AuditEntryID" = "OperationId"
             where ap."PropertyName" = 'PasswordHash'
             order by ap."AuditEntryID" desc
             limit 1) as "PasswordHash",
            (select ap."NewValue"
             from a."AuditEntryProperty" ap
             inner join operations
                on ap."AuditEntryID" = "OperationId"
             where ap."PropertyName" = 'PhoneNumber'
             order by ap."AuditEntryID" desc
             limit 1) as "PhoneNumber",
            (select ap."NewValue"
             from a."AuditEntryProperty" ap
             inner join operations
                on ap."AuditEntryID" = "OperationId"
             where ap."PropertyName" = 'SoftDeletedLevel'
             order by ap."AuditEntryID" desc
             limit 1) as "SoftDeletedLevel",
            (select ap."NewValue"
             from a."AuditEntryProperty" ap
             inner join operations
                on ap."AuditEntryID" = "OperationId"
             where ap."PropertyName" = 'UserName'
             order by ap."AuditEntryID" desc
             limit 1) as "UserName"
    )
select *
from initial_value
union all
select *
from current_value;