import java.util.HashMap;
import java.util.Map;

public class SymbolTable
{
    private Map<String, Integer> myMap;

    public SymbolTable () //constructor
    {
        myMap = new HashMap<>();
        for(int i =0; i<16;i ++)
        {
            myMap.put("R" + i,i);
        }
        myMap.put("SCREEN", 16384);
        myMap.put("KBD", 24576);
        myMap.put("SP", 0);
        myMap.put("LCL", 1);
        myMap.put("ARG", 2);
        myMap.put("THIS", 3);
        myMap.put("THAT", 4);
    }
    public void addEntry(String symbol,int address)
    {
        myMap.put(symbol,address);
    }


    public boolean contains(String symbol)
    {
        return myMap.containsKey(symbol);
    }

    public int getAddress(String symbol)
    {
        return myMap.get(symbol);
    }

}
