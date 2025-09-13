./odata-mcp --transport http https://services.odata.org/V2/Northwind/Northwind.svc/



./odata-mcp --api-key W4P3bPnpzGGrAPXPl2DQGweAKQlAcKga --transport http  https://sandbox.api.sap.com/sap/c4c/odata/v1/c4codataapi

./odata-mcp --api-key W4P3bPnpzGGrAPXPl2DQGweAKQlAcKga --transport http --http-addr 34.58.214.135:8080/ https://sandbox.api.sap.com/sap/c4c/odata/v1/c4codataapi

# Now works with --insecure:
./odata-mcp --api-key W4P3bPnpzGGrAPXPl2DQGweAKQlAcKga --transport http --http-addr 34.58.214.135:8080/ --insecure https://sandbox.api.sap.com/sap/c4c/odata/v1/c4codataapi

# Or with the original expert flag:
./odata-mcp --api-key W4P3bPnpzGGrAPXPl2DQGweAKQlAcKga --transport http --http-addr 34.58.214.135:8080/ --i-am-security-expert-i-know-what-i-am-doing https://sandbox.api.sap.com/sap/c4c/odata/v1/c4codataapi

