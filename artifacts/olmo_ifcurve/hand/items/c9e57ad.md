# Item c9e57ad

## Prompt (as the model received it)

Generate CSV data: The column names are ["ProductID", "Category", "Brand", "Price", "Stock"], the data should be comma delimited. Please generate 14 rows. Add one field which contains a special character and enclose it in double quotes.

## Verifiable constraints

- `custom:csv_special_character` {}: followed (official strict checker)

## Answer

ProductID,Category,Brand,Price,Stock  
1,Electronics,Samsung,300,50  
2,Clothing,Nike,150,30  
3,Books,Amazon,25,100  
4,Home,Furniture,200,20  
5,Toys,Legos,50,75  
6,Beauty,Keira,80,40  
7,"Electronics, Gadgets",Dell,400,15  
8,Food,Snack,5,200  
9,Tools,XYZ,20,10  
10,Toys,Barbie,30,60  
11,Furniture,Ikea,300,25  
12,Electronics,Apple,1500,5  
13,Books,Random House,40,80  
14,Clothing,Adidas,120,45
