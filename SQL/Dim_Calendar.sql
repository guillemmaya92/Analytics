-- Declarare variables
DECLARE @start_date DATE;
DECLARE @end_date DATE;
DECLARE @culture NVARCHAR(255) = 'en-EN';
-- Assign values to variables
SET @start_date = '2019-01-01';
SET @end_date = '2023-12-31';
-- Generate a data range
WITH DR AS (
SELECT
    date_range.date AS Date
FROM
(
    SELECT @start_date AS start_date, @end_date AS end_date
) date_params
CROSS APPLY (
    SELECT TOP (DATEDIFF(DAY, start_date, end_date) + 1)
        DATEADD(DAY, ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) - 1, start_date) AS date
    FROM
        sys.all_objects AS a
        CROSS JOIN sys.all_objects AS b
) date_range )
-- Define a calendar dimension
SELECT
	Date,
	CAST(DATEADD(DAY, 7 - DATEPART(WEEKDAY, Date), Date) AS DATE) as EOWeek,
	EOMONTH(Date) AS EOMonth,
	DATEFROMPARTS(YEAR(Date), 1, 1) AS EOYear,
	DAY(Date) AS Day,
	FORMAT(Date, 'dddd', @culture) AS Day_Name,
	FORMAT(Date, 'ddd', @culture) AS Day_Name_Abr,
	DATEPART(WEEKDAY, Date) AS WeekDay,
	DATEPART(WEEK, Date) AS WeekNum,
	MONTH(Date) AS Month,
	FORMAT(Date, 'MMMM', @culture) AS Month_Name,
	FORMAT(Date, 'MMM', @culture) AS Month_Name_Abr,
	DATEPART(QUARTER, Date) AS Quarter,
	'Q'+CONVERT(VARCHAR, DATEPART(QUARTER, Date)) AS Quarter_Name,
	DATEPART(QUARTER, Date)/2+1 AS Semester,
	'S'+CONVERT(VARCHAR, DATEPART(QUARTER, Date)/2+1) AS Semester_Name,
	YEAR(Date) AS Year,
	FORMAT(Date, 'yyyyMM', @culture) AS Year_Month,
	FORMAT(Date, 'MMM-yy', @culture) AS Year_Month_Name,
	CONVERT(INT, FORMAT(Date, 'yyyy') + FORMAT(DATEPART(WEEK, Date), '00')) AS Year_Week,
	FORMAT(Date, 'yy') + '-' + FORMAT(DATEPART(WEEK, Date), '00') AS Year_Week_Abr
FROM 
	DR