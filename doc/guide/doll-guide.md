
# Topic


# Topic Type
Raw
Distinct
Aggregate
Time
Ratio


# Pipeline

# Actions

# Insert or Merge Row

{snowflake}

# Conurrent Control 

# 1. Compatibility and Validation

Typically, value compatiblity is a complex issue which need to be considered seriously. To lighten the burden of this, most of these scenarios are built-in now.

## 1.1. Storage
### 1.1.1. Mapping of factor type and storage types
#### 1.1.1.1. MySQL
| \#  | Factor Type | Column Type   | Restrictions      |
| --- | ----------- | ------------- | ----------------- |
| 1   | SEQUENCE    | BIGINT        |
| 2   | NUMBER      | DECIMAL(32,6) |
| 3   | UNSIGNED    | DECIMAL(32,6) | 0, Positive Value |


#### 1.1.1.2. Oracle

#### 1.1.1.3. Mongo

### 1.1.2. Null or empty value
There is no `NOT-NULL` check in storage, which means any null or empty value can be stored.

> Null value occurring can be monitored in [Data Quality Center](path-to-the-dqc-doc.md#change-me-please), if it is concerned.

## 1.2. Pipeline Runtime
### 1.2.1. In expression
#### 1.2.1.1. `+`, `-`, `*`, `/`, `% (Modulo)`
Only works on numeric values.

#### 1.2.1.2. Date Functions
- Year Of
- Half Year Of
- Quarter Of
- Month Of
- Week Of Year
- Week Of Month
- Day of Month
- Day of Week

1. One and only one parameter is allowed,
2. When parameter is a factor, type must be one of `DATE`, `DATETIME`, `FULL_DATETIME`, `DATE_OF_BIRTH`,
3. When parameter is a constant or computed, value will be casted to string, and check by the following formats: 
   - YYYY/MM/DD
   - YYYY-MM-DD
   - 
4. Return value is treated as the following

| Function    | Return type   |
| ----------- | ------------- |
| YearOf      | YEAR          |
| HalfYearOf  | HALF_YEAR     |
| QuarterOf   | QUARTER       |
| MonthOf     | MONTH         |
| WeekOfYear  | WEEK_OF_YEAR  |
| WeekOfMonth | WEEK_OF_MONTH |
| DayOfMonth  | DAY_OF_MONTH  |
| DayOfWeek   | DAY_OF_WEEK   |

#### 1.2.1.3. =, !=
Any value can be compared with equals or not equals, by the following rules:
- Null value equals empty value,
- Values are compared after casting to string between differrent types,
- Milliseconds is ignored on comparing.

#### 1.2.1.4. >, >=, <, <=
Only date and numeric values are supported.

- Hour, minute, second and millisecond are ignored,
- String is compared after casting to date or number, depends on the type of another side.
- The following date formats are suppored:
   - YYYY/MM/DD
   - YYYY-MM-DD
   - 
#### 1.2.1.5. in, not in
Any value will be casted to string, and compare with the given options.

### 1.2.2. Variables in constant
- Use `{}` to introduce variables into constant definition,

```groovy
// there is a in-memory variable defined before this action
{premium}
```

- Multiple variables in one constant is allowed,

```groovy
{firstName}-{lastName}

// assume firstName=John, lastName=Doe
// output as below
// John-Doe
```

> Null value will be casted to empty string in multiple variables case.

- Use trigger data directly,

```groovy
// when premium is not defined in previous actions, try to find in trigger data.
// if there is a factor name is premium, retrieve its value.
// or there is no factor, use null value
{premium}
```

#### 1.2.2.1. Built-in Functions
- `&nextSeq`

- `&count`

- `&length`

- `&sum`

- `&old`

