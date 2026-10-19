from symbol_table import SymbolTable

st=SymbolTable()

print(st.insert("IDENTIFIER", "closet"))
print(st.insert("STRING", '"dress"'))
print(st.insert("NUMBER", "150"))

print(st.insert("IDENTIFIER", "closet"))


print(st.search("IDENTIFIER", "closet"))
print(st.search("IDENTIFIER", "budget"))

print("\nSymbol Table:")
for entry in st.get_entries():
    print(entry)

print("\nNumber of unique symbols:", len(st))