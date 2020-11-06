#include<unordered_map>
#include<iostream>
#include<vector>
#include<algorithm>
#include<cstring>
#include<cassert>
using namespace std;

int **create_array(int r , int c , int fill_val = 0){
    int **ret = new int*[r];
    for(int j = 0 ; j < r ; j++){
        ret[j] = new int[c];
        for(int i = 0 ; i < c ; i++){
            ret[j][i] = fill_val;
        }
    }
    return ret;
}


class DotsGame{
    int R , C;
    int fields , MAX_MASK;

    unordered_map < int , int > memo[2];

    enum CELL_STATE {
        FREE = 0,
        FIRST = 1,
        SECOND = 2,
    };


    void initialize(){
        fields = R * C;

        MAX_MASK = 1;
        for(int j = 0 ; j < fields ; j++)
            MAX_MASK *= 3;

        memo[0].clear();
        memo[1].clear();

    }

    // encode the array as a valid map key
    int encode(int **arr){

        int mask = 0;
        for(int r = 0 ; r < R ; r++)
            for(int c = 0 ; c < C ; c++)
                mask = (mask * 3) + arr[r][c];
        return mask;

    }

    // decode the map key
    int **decode(int mask){

        int **ret = create_array(R , C , 0);
        vector < int > bits;
        while(mask > 0){
            bits.push_back(mask % 3);
            mask /= 3;
        }
        while(bits.size() < fields) bits.push_back(0);
        for(int r = 0 ; r < R ; r++)
            for(int c = 0 ; c < C ; c++){
                ret[r][c] = bits.back();
                bits.pop_back();
            }
        return ret;

    }


    // output the grid
    void output(int **arr){
        for(int r = 0 ; r < R ; r++){
            for(int c = 0 ; c < C ; c++){
                if(arr[r][c] == CELL_STATE::FIRST)
                    cout<<'1';
                else if(arr[r][c] == CELL_STATE::SECOND)
                    cout<<'2';
                else if(arr[r][c] == CELL_STATE::FREE)
                    cout<<'.';
                cout<<' ';
            }
            cout<<endl;
        }
        pair < int , int > res = calc_score(arr);
        printf("Current scores, you have %d points, BOT allu has %d points\n",res.first,res.second);
    }


    int **depth = NULL , **low = NULL;
    vector < pair < int , int > > stck;

    int dx[8] = {0 , 0 , 1 , -1 , 1 , 1 , -1 , -1} , dy[8] = {1 , -1 , 0 , 0 , 1 , -1 , 1 , -1};
    int dfs_timer = 0;

    /*

    I use a tarjan approach to find cycles
    The logic is complicated to explain in comments needs drawing..etc
    Briefly:
    1- Do a dfs pushing nodes in a stack
    2- if a node has a back edge (other than dfs-tree edges) back to one of its ancestors then it's a part of a cycle
    3- if a node doesn't have a back edge check the stack if it's not at the top then there are nodes getting back to it and they all form a cycle (or part of a bigger cycle)
    4- if it's at the top then it's part of no-cycle just pop

    http://e-maxx.ru/algo/cutpoints
    https://cp-algorithms.com/graph/cutpoints.html

    */

    int dfs_cutpoints(int **arr , int x , int y , int px , int py){

        int ret = 0;


        depth[x][y] = ++dfs_timer;
        stck.push_back(make_pair(x , y));

        low[x][y] = depth[x][y];

        for(int d = 0 ; d < 8 ; d++){

            int nx = x + dx[d] , ny = y + dy[d];

            // still inside grid (not walls)
            if (nx < 0 || ny < 0 || nx >= R || ny >= C)
                continue;
            //
            if(nx == px && ny == py)
                continue;

            if(arr[nx][ny] != arr[x][y])
                continue;

            if(depth[nx][ny] == -1){
                ret += dfs_cutpoints(arr , nx , ny , x , y);
                low[x][y] = min(low[x][y] , low[nx][ny]);
            }
            else{
                low[x][y] = min(low[x][y] , depth[nx][ny]);
            }

        }


        if(depth[x][y] == low[x][y]){
            int cyc = 0;
            if(stck.back() != make_pair(x , y)){
                cyc = 1;
                while(stck.back() != make_pair(x , y)){
                    cyc++;
                    stck.pop_back();
                }
                stck.pop_back();
            }
            else stck.pop_back();

            ret += cyc;

        }

        return ret;
    }

public:

    void init(int _R , int _C){
        R = _R;
        C = _C;
        initialize();

    }

    //calculate the score of some grid
    pair < int , int > calc_score(int **arr){


        if(!depth){
            depth = create_array(R , C , -1);
            low = create_array(R , C , 0);
        }

        for(int r = 0 ; r < R ; r++){
            for(int c = 0 ; c < C ; c++){
                depth[r][c] = -1;
            }
        }

        stck.clear();
        dfs_timer = 0;

        int a_score = 0 , b_score = 0;


        for(int r = 0 ; r < R ; r++){
            for(int c = 0 ; c < C ; c++){

                if(depth[r][c] == -1){

                    if(arr[r][c] == CELL_STATE::FIRST)
                        a_score += dfs_cutpoints(arr , r , c , -1 , -1);
                    else if(arr[r][c] == CELL_STATE::SECOND)
                        b_score += dfs_cutpoints(arr , r , c , -1 , -1);
                }

            }
        }

        return make_pair(a_score , b_score);
    }


    int **current_grid;

    // make sure the move is ok
    int validate_move(int x , int y){
        if(x < 0 || y < 0 || x >= R || y >= C)
            return 2;
        if(current_grid[x][y] != CELL_STATE::FREE)
            return 3;
        return 1;
    }

    // check the best possible move for the bot
    pair < int , int > make_best_move(int **grid){
        int best = (1<<20);
        pair < int , int > ret = make_pair(-1 , -1);
        for(int r = 0 ; r < R ; r++){
            for(int c = 0 ; c < C ; c++){
                if(grid[r][c] != CELL_STATE::FREE)
                    continue;

                grid[r][c] = CELL_STATE::SECOND;
                if (best > min_max(encode(grid) , 0)){
                    best = min_max(encode(grid) , 0);
                    ret = make_pair(r , c);
                }
                grid[r][c] = CELL_STATE::FREE;

            }
        }
        assert(ret != make_pair(-1 , -1));
        return ret;
    }

    int min_max(int state , int player , int depth = 5){
        int **grid = decode(state);

        if(memo[player].find(state) != memo[player].end())
            return memo[player][state];


        int full_grid = 1;
        int &ret = memo[player][state];

        if(player == 0)
            ret = -(1<<20);
        else ret = (1<<20);

        for(int r = 0 ; r < R ; r++){
            for(int c = 0 ; c < C ; c++){

                if(grid[r][c] != CELL_STATE::FREE)
                    continue;

                full_grid = 0;

                if(player == 0){
                    grid[r][c] = CELL_STATE::FIRST;
                    ret = max(ret , min_max(encode(grid) , player ^ 1));
                }
                else{
                    grid[r][c] = CELL_STATE::SECOND;
                    ret = min(ret , min_max(encode(grid) , player ^ 1));
                }

                grid[r][c] = CELL_STATE::FREE;
            }
        }

        if(full_grid){
            pair < int , int > scores = calc_score(grid);
            ret = scores.first - scores.second;
            return ret;
        }

        return ret;

    }


    void run(){

        puts("Doing some precalculations");


        current_grid = create_array(R , C , 0);

        int remaining_fields = R * C;
        int player = 0;

        cout<<min_max(encode(current_grid) , 0)<<endl;

        puts("Simulation Started");

        output(current_grid);

        while(remaining_fields > 0){
            if(player == 0){

                int x = -1 , y = -1;
                puts("Enter 2 space separated values, row and column of your next move.");
                while(validate_move(x , y) != 1){
                    cin>>x>>y;
                    if(validate_move(x , y) == 2)
                        puts("You input invalid coordinates. repeat the input");
                    else if(validate_move(x , y) == 3)
                        puts("You are selecting an occupied cell. repeat the input");
                    else puts("Ok menss))");
                }
                current_grid[x][y] = CELL_STATE::FIRST;
                remaining_fields -= 1;
            }
            else{
                pair < int , int > next_move = make_best_move(current_grid);
                current_grid[next_move.first][next_move.second] = CELL_STATE::SECOND;
                remaining_fields -= 1;
            }
            output(current_grid);
            player ^= 1;
        }

        puts("Game ended, bye from BOT allu");

    }


}agent;

ostream& operator << (ostream &stream , pair < int , int > p){
    stream << p.first << ' ' << p.second << endl;
    return stream;
}


void test_1(){
    DotsGame test_agent;
    test_agent.init(4,4);

    pair < int , int > res;
    int **to_pass = create_array(4,4);

    /*
}
    test 1:

    1...
    .122
    .122
    1...

    scores should be 0-4
    */

    int test1[4][4] = {
        {1,0,0,0},
        {0,1,2,2},
        {0,1,2,2},
        {1,0,0,0}
    };
    for(int j = 0 ; j < 4 ; j++) for(int i = 0 ; i < 4 ; i++) to_pass[j][i] = test1[j][i];

    res = test_agent.calc_score(to_pass);
    assert(res == make_pair(0 , 4));
    puts("Test 1 passed");
}

void test_2(){
    // the game won't run for such constraints but just for checking cycle detection
    DotsGame test_agent;
    test_agent.init(10 , 10);

    pair < int , int > res;
    int **to_pass = create_array(10,10);

    /*
    test 1:


    ..........
    ..1..11111
    .11..1....
    ..1..22222
    ..11.2...2
    222222...2
    2......2.2
    2.....22.2
    2........2
    2222222222

    scores should be 9-33
    */

    int test[10][10] = {
        {0,0,0,0,0,0,0,0,0,0},
        {0,0,1,0,0,1,1,1,1,1},
        {0,1,1,0,0,1,0,0,0,0},
        {0,0,1,0,0,2,2,2,2,2},
        {0,0,1,1,0,2,0,0,0,2},
        {2,2,2,2,2,2,0,0,0,2},
        {2,0,0,0,0,0,0,2,0,2},
        {2,0,0,0,0,2,2,2,0,2},
        {2,0,0,0,0,0,0,0,0,2},
        {2,2,2,2,2,2,2,2,2,2},

    };
    for(int j = 0 ; j < 10 ; j++) for(int i = 0 ; i < 10 ; i++) to_pass[j][i] = test[j][i];

    res = test_agent.calc_score(to_pass);
    assert(res == make_pair(9 , 33));
    puts("Test 2 passed");
}

void test_3(){
    DotsGame test_agent;
    test_agent.init(4 , 4);

    pair < int , int > res;
    int **to_pass = create_array(4,4);

    /*
    test 1:


    1 2 2 2
    1 2 2 .
    1 1 2 2
    1 1 1 .


    scores should be 4 - 6
    */

    int test[4][4] = {
        {1,2,2,2},
        {1,2,2,0},
        {1,1,2,2},
        {1,1,1,0},

    };
    for(int j = 0 ; j < 4 ; j++) for(int i = 0 ; i < 4 ; i++) to_pass[j][i] = test[j][i];

    res = test_agent.calc_score(to_pass);
    //cout<<res<<endl;
    assert(res == make_pair(6 , 7));
    puts("Test 3 passed");

}
void run_tests(){
    test_1();
    test_2();
    test_3();


}
int main(){

    //freopen("in.in","r",stdin);

    run_tests();
    int R , C , FULL_TREE;
    puts("Enter the number of rows");
    cin>>R;
    puts("Enter the number of columns");
    cin>>C;
    puts("Rows are numbered from top to bottom starting from 0");
    puts("Columns are numbered from left to right starting from 0");
    agent.init(R , C);
    agent.run();
    return 0;



}
