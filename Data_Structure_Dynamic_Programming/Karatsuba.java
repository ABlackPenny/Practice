public class Karatsuba {
    /**
     * Karatsuba乘法
     */
    public static long karatsuba(String num1, String num2){
        //递归终止条件
        if(num1.length() < 10 || num2.length() < 10)
            return Long.parseLong(num1) * Long.parseLong(num2);

        // 计算拆分长度
        int size1 = num1.length();
        int size2 = num2.length();
        int halfN = Math.max(size1, size2) / 2;

        /* 拆分为a, b, c, d */
        String a = num1.substring(0, size1 - halfN);
        String b = num1.substring(size1 - halfN);
        String c = num2.substring(0, size2 - halfN);
        String d = num2.substring(size2 - halfN);

        // 计算z2, z0, z1, 此处的乘法使用递归
        long z2 = karatsuba(a, c);
        long z0 = karatsuba(b, d);
        long z1 = karatsuba((a + b), (c + d)) - z0 - z2;

        return (long)(z2 * Math.pow(10, (2*halfN)) + z1 * Math.pow(10, halfN) + z0);
    }

    public static void main(String[] args) {
        String num1 = "123423";
        String num2 = "32298332";
        System.out.println(karatsuba(num1, num2)); // 3986357030436
    }
}


