# DAX Pattern Library

Common DAX patterns organized by category. Reference this file when writing DAX measures.

## Time Intelligence

### Year-to-Date (YTD)
```dax
YTD Sales = TOTALYTD([Total Sales], 'Date'[Date])

-- With custom fiscal year end (June 30)
YTD Sales Fiscal = TOTALYTD([Total Sales], 'Date'[Date], "6/30")
```

### Month-to-Date (MTD)
```dax
MTD Sales = TOTALMTD([Total Sales], 'Date'[Date])
```

### Quarter-to-Date (QTD)
```dax
QTD Sales = TOTALQTD([Total Sales], 'Date'[Date])
```

### Previous Year comparison
```dax
PY Sales = CALCULATE([Total Sales], SAMEPERIODLASTYEAR('Date'[Date]))

YoY Growth =
VAR _Current = [Total Sales]
VAR _PY = [PY Sales]
RETURN
    DIVIDE(_Current - _PY, _PY)

YoY Growth % = FORMAT([YoY Growth], "0.0%")
```

### Previous Month
```dax
PM Sales = CALCULATE([Total Sales], DATEADD('Date'[Date], -1, MONTH))

MoM Growth =
VAR _Current = [Total Sales]
VAR _PM = [PM Sales]
RETURN
    DIVIDE(_Current - _PM, _PM)
```

### Rolling 12 months
```dax
Rolling 12M Sales =
CALCULATE(
    [Total Sales],
    DATESINPERIOD('Date'[Date], MAX('Date'[Date]), -12, MONTH)
)
```

### Rolling average
```dax
Rolling 3M Avg =
AVERAGEX(
    DATESINPERIOD('Date'[Date], MAX('Date'[Date]), -3, MONTH),
    CALCULATE([Total Sales])
)
```

### Year-over-year by month
```dax
Sales vs PY =
VAR _CurrentSales = [Total Sales]
VAR _PYSales = CALCULATE([Total Sales], SAMEPERIODLASTYEAR('Date'[Date]))
RETURN
    _CurrentSales - _PYSales
```

## Ranking

### Simple rank
```dax
Product Rank =
RANKX(
    ALL('Product'[ProductName]),
    [Total Sales],
    ,
    DESC,
    DENSE
)
```

### Top N filter
```dax
Is Top 10 =
VAR _Rank = [Product Rank]
RETURN
    IF(_Rank <= 10, 1, 0)

-- Use in a measure for Top N sales
Top 10 Sales =
CALCULATE(
    [Total Sales],
    TOPN(10, ALL('Product'[ProductName]), [Total Sales], DESC)
)
```

### Dynamic ranking with RANKX
```dax
Category Rank Within Region =
RANKX(
    ALLSELECTED('Product'[Category]),
    [Total Sales],
    ,
    DESC,
    DENSE
)
```

## Filtering

### Multiple OR conditions
```dax
Premium Sales =
CALCULATE(
    [Total Sales],
    'Product'[Category] IN {"Electronics", "Appliances", "Luxury"}
)
```

### Dynamic ALL / ALLSELECTED
```dax
-- % of grand total (ignores all filters on Product)
% of Total =
DIVIDE(
    [Total Sales],
    CALCULATE([Total Sales], ALL('Product'))
)

-- % of visible total (respects slicer selections)
% of Selected =
DIVIDE(
    [Total Sales],
    CALCULATE([Total Sales], ALLSELECTED('Product'))
)
```

### Conditional calculation
```dax
Sales with Discount =
CALCULATE(
    [Total Sales],
    'Sales'[DiscountPercent] > 0
)

Discount Rate =
DIVIDE([Sales with Discount], [Total Sales])
```

## Parent-Child Hierarchies

### Path functions
```dax
-- For org charts, account hierarchies, etc.
EmployeePath = PATH('Employee'[EmployeeID], 'Employee'[ManagerID])
Level = PATHLENGTH([EmployeePath])
Level1 = LOOKUPVALUE('Employee'[Name], 'Employee'[EmployeeID], PATHITEM([EmployeePath], 1, INTEGER))
Level2 = LOOKUPVALUE('Employee'[Name], 'Employee'[EmployeeID], PATHITEM([EmployeePath], 2, INTEGER))
```

## Dynamic Segmentation

### Value-based segments
```dax
Customer Segment =
VAR _Sales = [Total Sales]
RETURN
    SWITCH(
        TRUE(),
        _Sales >= 10000, "Platinum",
        _Sales >= 5000, "Gold",
        _Sales >= 1000, "Silver",
        "Bronze"
    )
```

### ABC analysis
```dax
ABC Class =
VAR _CumulativePct =
    DIVIDE(
        CALCULATE(
            [Total Sales],
            FILTER(
                ALL('Product'),
                [Product Rank] <= EARLIER([Product Rank])
            )
        ),
        CALCULATE([Total Sales], ALL('Product'))
    )
RETURN
    SWITCH(
        TRUE(),
        _CumulativePct <= 0.7, "A",
        _CumulativePct <= 0.9, "B",
        "C"
    )
```

## Semi-Additive Measures

### Last non-empty (for balances, inventory)
```dax
Closing Balance =
CALCULATE(
    LASTNONBLANK('Date'[Date], [Balance]),
    'Date'[Date]
)
```

### Opening balance
```dax
Opening Balance =
CALCULATE(
    [Closing Balance],
    PREVIOUSMONTH('Date'[Date])
)
```

## Statistical

### Moving average
```dax
7-Day Moving Avg =
AVERAGEX(
    DATESINPERIOD('Date'[Date], MAX('Date'[Date]), -7, DAY),
    [Daily Sales]
)
```

### Standard deviation
```dax
Sales StdDev =
VAR _Avg = AVERAGEX(ALL('Date'[Month]), [Total Sales])
RETURN
    SQRTX(
        AVERAGEX(
            ALL('Date'[Month]),
            ([Total Sales] - _Avg) ^ 2
        )
    )
```

### Median
```dax
Median Sales =
MEDIANX(
    ALL('Product'[ProductName]),
    [Total Sales]
)
```
